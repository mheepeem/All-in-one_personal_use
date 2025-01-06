from venv import logger

from pdfrw import PdfReader, PdfWriter, PageMerge, PdfDict, PdfName
import os
import pdfplumber
import pandas as pd
from config.logging_config import get_logger

logger = get_logger(__name__)

def create_dynamic_pages_per_sheet(input_pdf_path, output_pdf_path, pages_per_sheet=4, margin=5):
    """
    Create a new PDF where each sheet contains a specified number of pages
    of the input PDF, dynamically arranged and scaled without cropping.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_pdf_path (str): Path to the output PDF file.
        pages_per_sheet (int): Number of pages to fit per sheet (default is 4).
        margin (int): Margin between pages (default is 5 points).
    """
    # Load the input PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Dimensions for a Letter-sized landscape page
    page_width = 842  # Letter width in points (landscape)
    page_height = 595  # Letter height in points (landscape)

    # Determine grid layout
    rows = int(pages_per_sheet ** 0.5)
    cols = pages_per_sheet // rows

    quadrant_width = page_width / cols
    quadrant_height = page_height / rows

    for i in range(0, len(reader.pages), pages_per_sheet):
        # Create a new blank page
        new_page = PdfDict(
            Type=PdfName.Page,
            MediaBox=[0, 0, page_width, page_height],
            Resources=PdfDict(),
            Contents=[]
        )

        # Create a PageMerge object for the blank page
        page_merger = PageMerge(new_page)

        # Process up to pages_per_sheet pages from the original PDF
        for j in range(pages_per_sheet):
            if i + j < len(reader.pages):  # Ensure the page exists
                src_page = reader.pages[i + j]

                # Rotate the source page upright (if needed)
                src_page.Rotate = (int(src_page.inheritable.Rotate or 0)) % 360

                # Calculate position
                row = j // cols
                col = j % cols
                x_pos = col * quadrant_width + margin
                y_pos = page_height - ((row + 1) * quadrant_height) + margin

                # Scale to fit in the quadrant
                added_page = page_merger.add(src_page)
                scale_x = (quadrant_width - 2 * margin) / added_page[-1].w
                scale_y = (quadrant_height - 2 * margin) / added_page[-1].h
                scale = min(scale_x, scale_y)  # Preserve aspect ratio

                added_page[-1].scale(scale)
                added_page[-1].x = x_pos
                added_page[-1].y = y_pos

        # Render the merged page and add it to the writer
        writer.addpage(page_merger.render())

    # Save the final PDF
    writer.write(output_pdf_path)


def extract_tables_from_pdfs(pdf_paths, output_path=None, combine_files=True, combine_tables=True):
    """
    Extracts tables from one or more PDFs and saves them to Excel file(s).

    :param pdf_paths: List of PDF file paths to process
    :param output_path: Path to save the result(s). Can be a file or directory. If not specified, uses the same directory as the input file(s).
    :param combine_files: If True, combines results into a single Excel file. Otherwise, saves files separately.
    :param combine_tables: If True, combines all tables on the same page into one sheet. Otherwise, saves each table as a separate sheet.
    """
    try:
        # If output_path is not specified, use the same directory as the first input PDF
        if not output_path:
            first_pdf_directory = os.path.dirname(pdf_paths[0])
            if combine_files:
                output_path = os.path.join(first_pdf_directory, "combined_output.xlsx")
            else:
                output_path = first_pdf_directory  # Directory for individual files
            logger.info(f"No output path specified. Using default: {output_path}")

        results = {}  # Dictionary to store all results for combined output
        logger.info("Starting PDF table extraction process.")

        for pdf_path in pdf_paths:
            file_name = os.path.basename(pdf_path).rsplit('.', 1)[0]  # Get the file name without extension
            file_results = {}  # Store tables for the current PDF
            logger.info(f"Processing file: {pdf_path}")

            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)  # Get total number of pages
                logger.info(f"Total pages in the file: {total_pages}")  # Log the total pages

                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    if tables:
                        logger.info(f"Found {len(tables)} table(s) on page {i + 1}.")
                        if combine_tables:
                            combined_table = pd.DataFrame()
                            for table in tables:
                                df = pd.DataFrame(table)
                                combined_table = pd.concat([combined_table, df], ignore_index=True)
                            file_results[f"Page_{i + 1}"] = combined_table
                        else:
                            for j, table in enumerate(tables):
                                df = pd.DataFrame(table)
                                file_results[f"Page_{i + 1}_Table_{j + 1}"] = df
                    else:
                        logger.info(f"No tables found on page {i + 1}.")

            if combine_files:
                results[file_name] = file_results
            else:
                # Save individual file results
                individual_output = os.path.join(output_path, f"{file_name}.xlsx")
                with pd.ExcelWriter(individual_output, engine="openpyxl") as writer:
                    for sheet_name, table_df in file_results.items():
                        table_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                logger.info(f"Saved individual file to: {individual_output}")

        if combine_files:
            # Save all results into a single file
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for pdf_name, file_results in results.items():
                    for sheet_name, table_df in file_results.items():
                        sheet_name = f"{pdf_name}_{sheet_name}"[:31]  # Ensure sheet name is <= 31 chars
                        table_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
            logger.info(f"Combined results saved to: {output_path}")

        logger.info("PDF table extraction process completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise

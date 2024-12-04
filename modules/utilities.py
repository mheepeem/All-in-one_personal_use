from pdfrw import PdfReader, PdfWriter, PageMerge, PdfDict, PdfName


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

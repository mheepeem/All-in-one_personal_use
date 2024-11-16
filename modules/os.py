import mimetypes
import json
import chardet

#
def detect_encoding(file_path):
  try:
    with open(file_path, 'rb') as file:  # Open in binary mode for raw bytes
      raw_data = file.read()
      result = chardet.detect(raw_data)
      return result
  except FileNotFoundError:
    print(f"Error: File not found: {file_path}")
    return None
  except Exception as e:
    print(f"An error occurred: {e}")
    return None

#
def get_file_type(file_path):
  try:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type
  except Exception as e:
    print(f"Error determining file type: {e}")
    return None

#
def read_file(file_path, mode='r', encoding='utf-8'):
  try:
    # Detect encoding if not provided
    # with open(file_path, 'rb') as file:
    #   raw_data = file.read()
    #   encoding_info = chardet.detect(raw_data)
    #   encoding = encoding_info['encoding']

    with open(file_path, mode, encoding=encoding) as file:
      if mode == 'r':
        try:
          # Attempt to parse as JSON
          return json.load(file)
        except json.JSONDecodeError:
          # If not JSON, rewind and read as plain text
          file.seek(0)
          return file.read()
      elif mode == 'rb':
        return file.read()  # Return raw bytes for binary mode
      else:
        print(f"Unsupported file mode: {mode}")
        return None

  except FileNotFoundError:
    print(f"Error: File not found: {file_path}")
    return None
  except Exception as e:
    print(f"An error occurred: {e}")
    return None

#
def write_file(file_path, data, mode='w', encoding='utf-8'):
  try:
    if isinstance(data, (dict, list)):
      # If data is a dictionary or list, serialize it to JSON
      with open(file_path, mode, encoding=encoding) as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    elif isinstance(data, str):
      # If data is a string, write it directly in text mode
      with open(file_path, mode, encoding=encoding) as file:
        file.write(data)
    elif isinstance(data, bytes):
      # If data is bytes, write it directly in binary mode
      with open(file_path, mode) as file:  # No encoding needed for binary
        file.write(data)
    else:
      print(f"Unsupported data type: {type(data)}")

  except Exception as e:
    print(f"An error occurred: {e}")

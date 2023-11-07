import csv
import base64
import os

with open('../2-Textract/data/suspects/suspects.csv', 'r') as infile, open('../2-Textract/data/suspects/cleaned_suspects.csv', 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write the first row (header) directly to the output file
    writer.writerow(next(reader))

    for row in reader:
        try:
            cell = row[0]
            # Try to decode the first cell
            decoded_cell = base64.b64decode(cell).decode('utf-8')
            # Encode the cell before writing
            encoded_cell = base64.b64encode(decoded_cell.encode('utf-8')).decode('utf-8')
            # Write the encoded cell and the rest of the row to the new file
            writer.writerow([encoded_cell] + row[1:])
        except Exception:
            # Skip the row if the first cell cannot be decoded
            continue

# Delete the original suspects.csv file
os.remove('../2-Textract/data/suspects/suspects.csv')

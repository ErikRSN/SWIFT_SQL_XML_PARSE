import sqlite3
import xml.etree.ElementTree as ET

def parse(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Namespace for pain.001.001.03
    ns = {'': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03'}

    payments = []
    for payment_info in root.findall('.//PmtInf', ns):
        instruction_id = payment_info.find('PmtInfId', ns).text

        for credit_transfer in payment_info.findall('.//CdtTrfTxInf', ns):
            end_to_end_id = credit_transfer.find('PmtId/EndToEndId', ns).text
            amount = credit_transfer.find('Amt/InstdAmt', ns).text
            currency = credit_transfer.find('Amt/InstdAmt', ns).attrib['Ccy']

            debtor_name_element = credit_transfer.find('Dbtr/Nm', ns)
            debtor_name = debtor_name_element.text if debtor_name_element is not None else "Unknown"

            creditor_name_element = credit_transfer.find('Cdtr/Nm', ns)
            creditor_name = creditor_name_element.text if creditor_name_element is not None else "Unknown"

            payments.append({
                'instruction_id': instruction_id,
                'end_to_end_id': end_to_end_id,
                'amount': amount,
                'currency': currency,
                'debtor_name': debtor_name,
                'creditor_name': creditor_name,
                'transaction_date': root.find('.//CreDtTm', ns).text.split('T')[0]
            })
    return payments

def insert_payments(payments):
    # Connect to the SQLite database
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()

    # Create the Payments table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instruction_id TEXT,
            end_to_end_id TEXT,
            amount REAL,
            currency TEXT,
            debtor_name TEXT,
            creditor_name TEXT,
            transaction_date TEXT
        )
    ''')

    # Insert payment data into the Payments table
    for payment in payments:
        cursor.execute('''
            INSERT INTO Payments (instruction_id, end_to_end_id, amount, currency, debtor_name, creditor_name, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (payment['instruction_id'], payment['end_to_end_id'], payment['amount'], payment['currency'], payment['debtor_name'], payment['creditor_name'], payment['transaction_date']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def main():
    xml_file = 'C:\\edu\\xml\\pain.001.001.03.xml'
    payments = parse(xml_file)
    insert_payments(payments)
    print("Data inserted successfully.")

if __name__ == "__main__":
    main()
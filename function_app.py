import logging
import os
from datetime import datetime, timezone

import azure.functions as func
from azure.data.tables import TableServiceClient


app = func.FunctionApp()


@app.function_name(name="ProcessInvoice")
@app.blob_trigger(
    arg_name="invoice",
    path="incoming-invoices/{name}",
    connection="AzureWebJobsStorage",
    source="EventGrid",
)
@app.blob_output(
    arg_name="processed_invoice",
    path="processed-invoices/{name}",
    connection="AzureWebJobsStorage",
)
def process_invoice(
    invoice: func.InputStream,
    processed_invoice: func.Out[bytes],
) -> None:
    """Copy a new PDF and record its processing result in Table Storage."""
    filename = os.path.basename(invoice.name)
    file_data = invoice.read()

    if not filename.lower().endswith(".pdf"):
        logging.warning("Skipped non-PDF file: %s", filename)
        return

    processed_invoice.set(file_data)

    connection_string = os.environ["AzureWebJobsStorage"]
    table_service = TableServiceClient.from_connection_string(connection_string)
    table = table_service.create_table_if_not_exists("InvoiceProcessingLog")

    now = datetime.now(timezone.utc)
    table.upsert_entity(
        {
            "PartitionKey": "Invoices",
            "RowKey": f"{now.strftime('%Y%m%d%H%M%S%f')}-{filename}",
            "FileName": filename,
            "FileSizeBytes": len(file_data),
            "ProcessedAtUtc": now.isoformat(),
            "Status": "Processed",
        }
    )

    logging.info("Processed invoice %s (%d bytes)", filename, len(file_data))

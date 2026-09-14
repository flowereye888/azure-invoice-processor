# Automatic PDF Invoice Processor

When a PDF is uploaded to `incoming-invoices`, the Azure Function:

1. Copies it to `processed-invoices`.
2. Adds a processing record to the `InvoiceProcessingLog` Azure table.

The function uses the Python v2 programming model and an Event Grid-based blob trigger.

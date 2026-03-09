import { SQSClient, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';
import { UpdateAvailabilityHandler } from '../../application/command/UpdateAvailabilityHandler';
import { CancelEventBookingsHandler } from '../../application/command/CancelEventBookingsHandler';

export class SqsEventConsumer {
  private running = false;

  constructor(
    private readonly sqsClient: SQSClient,
    private readonly queueUrl: string,
    private readonly updateAvailabilityHandler: UpdateAvailabilityHandler,
    private readonly cancelEventBookingsHandler: CancelEventBookingsHandler
  ) {}

  async start(): Promise<void> {
    this.running = true;
    console.log(`🔄 SQS Consumer started, polling: ${this.queueUrl}`);
    
    while (this.running) {
      try {
        await this.pollMessages();
      } catch (error) {
        console.error('❌ Error polling SQS:', error);
        await this.sleep(5000);
      }
    }
  }

  stop(): void {
    this.running = false;
    console.log('⏹️ SQS Consumer stopped');
  }

  private async pollMessages(): Promise<void> {
    const response = await this.sqsClient.send(new ReceiveMessageCommand({
      QueueUrl: this.queueUrl,
      MaxNumberOfMessages: 10,
      WaitTimeSeconds: 20,
      MessageAttributeNames: ['All'],
    }));

    if (!response.Messages || response.Messages.length === 0) {
      return;
    }

    for (const message of response.Messages) {
      try {
        await this.processMessage(message);
        
        // Delete message after successful processing
        if (message.ReceiptHandle) {
          await this.sqsClient.send(new DeleteMessageCommand({
            QueueUrl: this.queueUrl,
            ReceiptHandle: message.ReceiptHandle,
          }));
        }
      } catch (error) {
        console.error(`❌ Error processing message ${message.MessageId}:`, error);
        // Message will return to queue after visibility timeout
      }
    }
  }

  private async processMessage(message: any): Promise<void> {
    const body = JSON.parse(message.Body || '{}');
    
    // EventBridge wraps events — extract detail-type and detail
    const detailType = body['detail-type'] || body.detailType;
    const detail = body.detail || body;

    console.log(`📨 Received event: ${detailType}`);

    switch (detailType) {
      case 'EventCreated':
        await this.updateAvailabilityHandler.handle({
          eventId: detail.eventId || detail.id,
          name: detail.name || 'Unknown Event',
          capacity: detail.capacity || detail.totalCapacity || 0,
          eventDate: detail.eventDate || new Date().toISOString(),
        });
        console.log(`✅ Processed EventCreated for event ${detail.eventId || detail.id}`);
        break;

      case 'EventCancelled':
        const count = await this.cancelEventBookingsHandler.handle({
          eventId: detail.eventId || detail.id,
          reason: detail.reason || 'Event cancelled',
        });
        console.log(`✅ Processed EventCancelled: ${count} bookings cancelled`);
        break;

      default:
        console.log(`⚠️ Unknown event type: ${detailType}, skipping`);
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

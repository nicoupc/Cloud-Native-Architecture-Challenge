import { CloudWatchLogsClient, PutLogEventsCommand } from '@aws-sdk/client-cloudwatch-logs';

const LOG_GROUP = '/aws/booking-service';
const LOG_STREAM = 'booking-service';

let cloudwatchClient: CloudWatchLogsClient | null = null;
let sequenceToken: string | undefined;
let logBuffer: string[] = [];
let flushTimer: NodeJS.Timeout | null = null;

function getClient(): CloudWatchLogsClient {
  if (!cloudwatchClient) {
    const isLocalStack = process.env.USE_LOCALSTACK !== 'false';
    const endpoint = process.env.LOCALSTACK_ENDPOINT || 'http://localhost:4566';

    cloudwatchClient = new CloudWatchLogsClient({
      ...(isLocalStack ? {
        endpoint,
        credentials: { accessKeyId: 'test', secretAccessKey: 'test' },
      } : {}),
      region: process.env.AWS_REGION || 'us-east-1',
    });
  }
  return cloudwatchClient;
}

async function flushLogs(): Promise<void> {
  if (logBuffer.length === 0) return;

  const events = logBuffer.map(msg => ({
    message: msg,
    timestamp: Date.now(),
  }));
  logBuffer = [];

  try {
    await getClient().send(new PutLogEventsCommand({
      logGroupName: LOG_GROUP,
      logStreamName: LOG_STREAM,
      logEvents: events,
      sequenceToken,
    }));
  } catch (error: any) {
    // Silently fail — console still has the logs
  }
}

export const logger = {
  info: (message: string, meta?: Record<string, any>) => {
    const formatted = meta ? `${message} ${JSON.stringify(meta)}` : message;
    console.log(`[INFO] ${formatted}`);
    logBuffer.push(`[INFO] ${formatted}`);
    if (!flushTimer) flushTimer = setTimeout(() => { flushTimer = null; flushLogs(); }, 5000);
  },
  error: (message: string, meta?: Record<string, any>) => {
    const formatted = meta ? `${message} ${JSON.stringify(meta)}` : message;
    console.error(`[ERROR] ${formatted}`);
    logBuffer.push(`[ERROR] ${formatted}`);
    if (!flushTimer) flushTimer = setTimeout(() => { flushTimer = null; flushLogs(); }, 1000);
  },
  warn: (message: string, meta?: Record<string, any>) => {
    const formatted = meta ? `${message} ${JSON.stringify(meta)}` : message;
    console.warn(`[WARN] ${formatted}`);
    logBuffer.push(`[WARN] ${formatted}`);
  },
  debug: (message: string, meta?: Record<string, any>) => {
    const formatted = meta ? `${message} ${JSON.stringify(meta)}` : message;
    console.debug(`[DEBUG] ${formatted}`);
  },
};

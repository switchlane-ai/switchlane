import { afterEach, describe, expect, it, vi } from 'vitest';
import { Switchlane } from '../sdk/src/index.js';

describe('TypeScript SDK base URL', () => {
  afterEach(() => vi.restoreAllMocks());

  it.each([
    [undefined, 'https://switchlane.ai/v1/route'],
    ['https://example.test/', 'https://example.test/v1/route'],
  ])('routes through %s', async (baseUrl, expectedUrl) => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ recommendations: [] }), {
        headers: { 'Content-Type': 'application/json' },
      })
    );
    const client = new Switchlane({ apiKey: 'sl_live_test', baseUrl });

    await client.route('unknown task');

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy).toHaveBeenCalledWith(expectedUrl, expect.objectContaining({
      method: 'POST',
      headers: expect.objectContaining({ Authorization: 'Bearer sl_live_test' }),
    }));
  });
});
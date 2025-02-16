const path = require("path");
const { Pact } = require("@pact-foundation/pact");
const axios = require("axios");

const provider = new Pact({
  consumer: "ConsumerService",
  provider: "ProviderService",
  port: 1234,
  log: path.resolve(__dirname, "logs", "pact.log"),
  dir: path.resolve(__dirname, "../pacts"),
  spec: 2,
});

describe("Pact with ProviderService", () => {
  beforeAll(() => provider.setup());

  afterAll(() => provider.finalize());

  test("should return a successful response", async () => {
    await provider.addInteraction({
      state: "data exists",
      uponReceiving: "a request for data",
      withRequest: {
        method: "GET",
        path: "/data",
      },
      willRespondWith: {
        status: 200,
        body: { message: "Success" },
      },
    });

    // Make request to mock server
    const response = await axios.get("http://localhost:1234/data");
    expect(response.status).toBe(200);
    expect(response.data.message).toBe("Success");

    // Verify the interaction
    await provider.verify();
  });
});

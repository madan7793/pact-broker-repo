const pact = require("@pact-foundation/pact");
const axios = require("axios");
const { like } = pact.Matchers;
const getPort = require("get-port");

let provider;

beforeAll(async () => {
  const port = await getPort({ port: 3000 }); // Ensure the port is available

  provider = new pact.Pact({
    consumer: "FrontendApp",
    provider: "UserService",
    port: port,  // Dynamically assign an available port
    log: "./logs/pact.log",
    dir: "./pacts",
    spec: 2,
  });

  await provider.setup();
});

afterAll(async () => {
  await provider.finalize();
});

describe("Pact with ProviderService", () => {
  it("should return a successful response", async () => {
    await provider.addInteraction({
      state: "Provider is available",
      uponReceiving: "A request for data",
      withRequest: {
        method: "GET",
        path: "/data",
      },
      willRespondWith: {
        status: 200,
        body: { message: "Success" },
      },
    });

    const response = await axios.get(`http://localhost:${provider.opts.port}/data`);
    expect(response.status).toBe(200);
    expect(response.data.message).toBe("Success");
  });
});

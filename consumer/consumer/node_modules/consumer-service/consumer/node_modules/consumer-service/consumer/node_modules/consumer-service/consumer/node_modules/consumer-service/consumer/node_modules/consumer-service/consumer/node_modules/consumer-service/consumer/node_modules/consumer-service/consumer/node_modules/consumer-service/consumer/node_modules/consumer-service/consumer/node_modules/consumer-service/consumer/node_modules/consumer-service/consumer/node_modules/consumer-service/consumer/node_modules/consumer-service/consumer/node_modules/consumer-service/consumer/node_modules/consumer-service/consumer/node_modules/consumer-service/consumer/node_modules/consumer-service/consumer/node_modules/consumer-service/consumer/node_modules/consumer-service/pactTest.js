const pact = require('@pact-foundation/pact');
const { like } = pact.Matchers;
const provider = new pact.Pact({ consumer: 'FrontendApp', provider: 'UserService' });

describe('Pact with UserService', () => {
    beforeAll(() => provider.setup());
    afterAll(() => provider.finalize());

    it('should fetch user details', async () => {
        await provider.addInteraction({
            state: 'User exists',
            uponReceiving: 'A request for user details',
            withRequest: { method: 'GET', path: '/users/1' },
            willRespondWith: { status: 200, body: like({ id: 1, name: 'John Doe' }) },
        });
    });
});
Feature: Pact Consumer Test
  Scenario: Consumer makes a request to provider
    Given a provider exists
    When the consumer makes a request
    Then the provider should return a valid response

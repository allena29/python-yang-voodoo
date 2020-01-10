Feature: Basic Datastore
    
    
  Scenario: 01. Opening and closing a daemon

  
    Given we stop any 'integrationtest' datastore-bridges
    And we delete any existing data for 'integrationtest'
    And we start a datastore-bridge for 'integrationtest'

    Then the following file should exist pid/integrationtest.pid
    And the following file should not exist datastore/integrationtest.persist

	

    
  Scenario: 02. Opening a daemon and setting data with a client

  
    Given we stop any 'integrationtest' datastore-bridges
    And we delete any existing data for 'integrationtest'
    And we start a datastore-bridge for 'integrationtest'

    When we start a new candidate transaction for 'integrationtest'
    Then we should be given a transaction-id.
	

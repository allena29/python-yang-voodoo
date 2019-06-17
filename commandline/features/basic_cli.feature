Feature: Basic CLI mode validations against test data structures

  Scenario: Login to the CLI and poke around operational mode

    When we open the command line interface
    Then we should be presented with a welcome prompt containing
      """
      Welcome goes here
      """

    When we send the following commands
      """
      configure
      """
    Then we should be in configuration mode

    When we send the following configuration commands
      """
      set cli a apple horrible

      """


    When we send the following commands
      """
      exit
      """

    Then we should be in operational mode

    When we send the following commands
      """
      exit
      """
    Then the command line should have cleanly closed

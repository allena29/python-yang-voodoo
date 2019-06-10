Feature: Basic CLI mode validations against test data structures

  Scenario: Login to the CLI and poke around operational mode

    When we open the command line interface
    Then we should be presented with a welcome prompt containing
      """
      Welcome goes here
      """

    When we send the following command
      """
      configure
      """
    Then we should be in configuration mode

    When we send the following command
      """
      set cli a apple
      """


    When we send the following command
      """
      exit
      """

    Then we should be in operational mode

    When we send the following command
      """
      exit
      """
    Then the command line should have cleanly closed

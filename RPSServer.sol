// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.6;


contract RPSGame {
    // GameState - INITIATED after inital game setup, RESPONDED after responder adds hash choice, WIN or DRAW after final scoring
    enum RPSGameState {INITIATED, RESPONDED, WIN, DRAW}

    // PlayerState - PENDING until they add hashed choice, PLAYED after adding hash choice, CHOICE_STORED once raw choice and random string are stored
    enum PlayerState {PENDING, PLAYED, CHOICE_STORED}

    // 0 before choices are stored, 1 for Rock, 2 for Paper, 3 for Scissors. Strings are stored only to generate comment with choice names
    string[4] choiceMap = ['None', 'Rock', 'Paper', 'Scissors'];

    struct RPSGameData {
        address initiator; // Address of the initiator
        PlayerState initiator_state; // State of the initiator
        bytes32 initiator_hash; // Hashed choice of the initiator
        uint8 initiator_choice; // Raw number of initiator's choice - 1 for Rock, 2 for Paper, 3 for Scissors
        string initiator_random_str; // Random string chosen by the initiator

	address responder; // Address of the responder
        PlayerState responder_state; // State of the responder
        bytes32 responder_hash; // Hashed choice of the responder
        uint8 responder_choice; // Raw number of responder's choice - 1 for Rock, 2 for Paper, 3 for Scissors
        string responder_random_str; // Random string chosen by the responder

        RPSGameState state; // Game State
        address winner; // Address of winner after completion. addresss(0) in case of draw
        string comment; // Comment specifying what happened in the game after completion
    }

    RPSGameData _gameData;

    // Initiator sets up the game and stores its hashed choice in the creation itself. Game and player states are adjusted accordingly
    constructor(address _initiator, address _responder, bytes32 _initiator_hash) {
        _gameData = RPSGameData({
                                    initiator: _initiator,
                                    initiator_state: PlayerState.PLAYED,
                                    initiator_hash: _initiator_hash,
                                    initiator_choice: 0,
                                    initiator_random_str: '',
                                    responder: _responder,
                                    responder_state: PlayerState.PENDING,
                                    responder_hash: 0,
                                    responder_choice: 0,
                                    responder_random_str: '',
                                    state: RPSGameState.INITIATED,
                                    winner: address(0),
                                    comment: ''
                            });
    }

    // Responder stores their hashed choice. Game and player states are adjusted accordingly.
    function addResponse(bytes32 _responder_hash) public {
        require(_gameData.state == RPSGameState.INITIATED, "Error: Game has not been initiated or already been completed");

        _gameData.responder_hash = _responder_hash;
        _gameData.state = RPSGameState.RESPONDED;
        _gameData.responder_state = PlayerState.PLAYED;
    }

    // Initiator adds raw choice number and random string. If responder has already done the same, the game should process the completion execution
    function addInitiatorChoice(uint8 _choice, string memory _randomStr) public returns (bool) {

        require( _gameData.state == RPSGameState.RESPONDED, "Error: Responder has not responded or game already completed");
        require( _gameData.initiator_state == PlayerState.PLAYED, "Error: Either early or already done");
        _gameData.initiator_choice = _choice;
        _gameData.initiator_random_str = _randomStr;
        _gameData.initiator_state = PlayerState.CHOICE_STORED;
        if (_gameData.responder_state == PlayerState.CHOICE_STORED) {
            __validateAndExecute();
        }
        return true;
    }

    // Responder adds raw choice number and random string. If initiator has already done the same, the game should process the completion execution
    function addResponderChoice(uint8 _choice, string memory _randomStr) public returns (bool) {
        require(_gameData.state == RPSGameState.RESPONDED, "Error: Responder has not responded  or game already completed");
        require( _gameData. responder_state == PlayerState.PLAYED, "Error: Either early or already done");
        _gameData.responder_choice = _choice;
        _gameData.responder_random_str = _randomStr;
        _gameData.responder_state = PlayerState.CHOICE_STORED;
        if (_gameData.initiator_state == PlayerState.CHOICE_STORED) {
            __validateAndExecute();
        }
        return true;
    }

    // Core game logic to check raw choices against stored hashes, and then the actual choice comparison
    // Can be split into multiple functions internally
    function __validateAndExecute() private {
        bytes32 initiatorCalcHash = sha256(abi.encodePacked(choiceMap[_gameData.initiator_choice], '-', _gameData.initiator_random_str));
        bytes32 responderCalcHash = sha256(abi.encodePacked(choiceMap[_gameData.responder_choice], '-', _gameData.responder_random_str));
        bool initiatorAttempt = false;
        bool responderAttempt = false;


        if ((initiatorCalcHash != _gameData.initiator_hash)&& (responderCalcHash == _gameData.responder_hash) ){
            initiatorAttempt = false;
            responderAttempt = true;
            _gameData.winner=_gameData.responder;
            _gameData.state=RPSGameState.WIN;
            _gameData.comment="Responder won as Initiator's hash did not match";}
        else if ((initiatorCalcHash == _gameData.initiator_hash)&& (responderCalcHash != _gameData.responder_hash) ){
            initiatorAttempt = true;
            responderAttempt = false;
            _gameData.winner=_gameData.initiator;
            _gameData.state=RPSGameState.WIN;
            _gameData.comment="Initiator won as responders hash did not match";}
        else if ((initiatorCalcHash != _gameData.initiator_hash)&& (responderCalcHash != _gameData.responder_hash)) {
            initiatorAttempt = false;
            responderAttempt = false;
            _gameData.winner=address(0);
            _gameData.state=RPSGameState.DRAW;
            _gameData.comment="The game is draw as both hashes did not match";}

             // Add logic to complete the game first based on attempt validation states, and then based on actual game logic if both attempts are validation
        // Comments can be set appropriately like 'Initator attempt invalid', or 'Scissor beats Paper', etc.

        else  {
            initiatorAttempt = true;
            responderAttempt = true;
            if (_gameData.initiator_choice==_gameData.responder_choice){
                _gameData.winner=address(0);
                _gameData.state=RPSGameState.DRAW;
                _gameData.comment="The result is draw as both made the same choice";
        }
            else if (_gameData.initiator_choice==1 &&_gameData.responder_choice==2 ){

                _gameData.state=RPSGameState.WIN;
                _gameData.comment="Responder won as Responder selected Paper while Initiator selected Rock ";
                _gameData.winner=_gameData.responder;}
            else if (_gameData.initiator_choice==1 &&_gameData.responder_choice==3){

                _gameData.state=RPSGameState.WIN;
                _gameData.comment="Initiator won as Responder selected Scissors while Initiator selected Rock";
                _gameData.winner=_gameData.initiator;}
            else if (_gameData.initiator_choice==2 &&_gameData.responder_choice==1 ){

                _gameData.state=RPSGameState.WIN;
                _gameData.comment="Initiator won as Responder selected Rock while Initiator selected Paper";
                _gameData.winner=_gameData.initiator;}
            else if (_gameData.initiator_choice==2 &&_gameData.responder_choice==3){

                _gameData.state=RPSGameState.WIN;
                _gameData.comment="Responder won as Responder selected Scissors while Initiator selected Paper";
                _gameData.winner=_gameData.responder;}
            else if (_gameData.initiator_choice==3 &&_gameData.responder_choice==1 ){

                _gameData.state=RPSGameState.WIN;
                _gameData.comment="Responder won as Responder selected Rock while Initiator selected Scissors";
                _gameData.winner=_gameData.responder;}
            else if (_gameData.initiator_choice==3 &&_gameData.responder_choice==2){

                _gameData.state=RPSGameState.WIN;
                _gameData.comment="Initiator won as Responder selected Paper while Initiator selected Scissors";
                _gameData.winner=_gameData.initiator;}

        }



    }


    // Returns the address of the winner, GameState (2 for WIN, 3 for DRAW), and the comment
    function getResult() public view returns (address, RPSGameState, string memory) {

        require( _gameData.state == RPSGameState.WIN|| _gameData.state == RPSGameState.DRAW, "Error: Game in progress,results will take time");

        return (_gameData.winner, _gameData.state, _gameData.comment);
    }



}


contract RPSServer {
    // Mapping for each game instance with the first address being the initiator and internal key aaddress being the responder
    mapping(address => mapping(address => RPSGame)) _gameList;

    modifier validAddress(address _playerAdd) {
        require(msg.sender != _playerAdd, "Initiator and Responder cannot be same");
        require(_playerAdd != address(0), "Error, cannot be zero address");

        _;
    }
    modifier validChoice(uint8 _playerChoice) {
        require(_playerChoice>=1 && _playerChoice<=3 , "Error, Please select 1 for Rock, 2 for Paper,3 for Scissors");

        _;
    }




    // Initiator sets up the game and stores its hashed choice in the creation itself. New game created and appropriate function called
    function initiateGame(address _responder, bytes32 _initiator_hash)public validAddress(_responder)  {

        RPSGame game = new RPSGame(msg.sender, _responder, _initiator_hash)  ;

        _gameList[msg.sender][_responder] = game;




    }// end of intiateGame function

    // Responder stores their hashed choice. Appropriate RPSGame function called
    function respond(address _initiator, bytes32 _responder_hash) public validAddress(_initiator)   {


        RPSGame game = _gameList[_initiator][msg.sender];
        game.addResponse(_responder_hash);
    }

    // Initiator adds raw choice number and random string. Appropriate RPSGame function called
    function addInitiatorChoice(address _responder, uint8 _choice, string memory _randomStr) public validAddress(_responder) validChoice(_choice) returns (bool) {

        RPSGame game = _gameList[msg.sender][_responder];
        return game.addInitiatorChoice(_choice, _randomStr);
    }

    // Responder adds raw choice number and random string. Appropriate RPSGame function called
    function addResponderChoice(address _initiator, uint8 _choice, string memory _randomStr) public validAddress(_initiator) validChoice(_choice) returns (bool) {
        RPSGame game = _gameList[_initiator][msg.sender];
        return game.addResponderChoice(_choice, _randomStr);
    }

    // Result details request by the initiator
    function getInitiatorResult(address _responder)  public validAddress(_responder) view returns (address, RPSGame.RPSGameState, string memory) {
        RPSGame game = _gameList[msg.sender][_responder];
        return game.getResult();
    }

    // Result details request by the responder
    function getResponderResult(address _initiator)  public validAddress(_initiator)  view returns (address, RPSGame.RPSGameState, string memory) {
        RPSGame game = _gameList[_initiator][msg.sender];
        return game.getResult();
    }
}








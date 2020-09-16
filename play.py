import threading, berserk, sys, chess, re
from redisClient import RedisClient
from nltk.probability import FreqDist, MLEProbDist

class Game(threading.Thread):
    def __init__(self, client, game_id, **kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id
        self.client = client
        self.stream = client.bots.stream_game_state(game_id)
        self.current_state = next(self.stream)
        self.board = chess.Board()
        self.color = None
        self.opponent_color = None
        self.opponent_elo = 1500
        self.countPushes = 0
        self.rclient = RedisClient()


    def run(self):
        print("Run")
        sys.stdout.flush()
        for event in client.bots.stream_game_state(self.game_id):
            print(event)
            if (event['type'] == 'gameFull'):
                moves = event['state']['moves'].split(' ')
                self.generateBoardFen(moves)
                self.setBotPlayer(event)
                self.opponent_elo = event[self.opponent_color]['rating']
                print('board fen: '+ self.board.board_fen())
            elif event['type'] == 'gameState'and self.color_to_play(event) == self.color:
                self.handle_state_change(event)

    def color_to_play(self, event):
        moves = event['moves'].split(' ')
        nb_moves = len(moves)
        if nb_moves % 2 == 1:
            return 'black'
        return 'white'




    def setBotPlayer(self, event):
        if event['white']['id'] == 'patinside_bot':
            self.color = 'white'
            self.opponent_color = 'black'

        else:
            self.color = 'black'
            self.opponent_color = 'white'


    def handle_state_change(self, event):
        print("Handle State change")
        last_move = event['moves'].split(' ')[-1]
        print('last move: ' + last_move)
        self.updateBoardFen(last_move)
        key = str(chess.polyglot.zobrist_hash(self.board))
        print("key: " + key)
        db_result = self.rclient.conn.hgetall(key)
        print("db_result: " + str(db_result))
        if len(db_result) == 0:
            print("No key found for pattern for board: " + str(self.board.board_fen()))
        else:
            next_move_keys = dict.keys(db_result)
            print("will calculate a move")
            elo_fen_tuple = ([re.split(":", str(x)) for x in db_keys])
            elo_fen_tuple = [[abs(int(item[0][2:]) - self.opponent_elo//100), item] for item in elo_fen_tuple]
            closest_key = ":".join(elo_fen_tuple[0][1])
            closest_key = closest_key[2:-1]
            next_move_candidates = self.rclient.conn.hgetall(closest_key)


        next_move_candidates = {y.decode('ascii'): int(next_move_candidates.get(y).decode('ascii')) for y in
                                next_move_candidates.keys()}
        print("next_move_candidates: " + str(next_move_candidates))
        freq_dist = FreqDist(next_move_candidates)
        prob_dist = MLEProbDist(freq_dist)
        next_move = chess.Move.from_uci(prob_dist.generate())
        print("next_move :" + str(next_move))
        client.bots.make_move(self.game_id, next_move)



    def generateBoardFen(self, moves):
        boardFen = chess.Board()
        if moves != ['']:
            for move in moves:
                move = chess.Move.from_uci(move)
                boardFen.push(move)
        self.board = boardFen


    def updateBoardFen(self, move):
        move = chess.Move.from_uci(move)
        self.board.push(move)


    def handle_chat_line(self, chat_line):
        pass


session = berserk.TokenSession("Vpog1WSAM9o3nbT2")
client = berserk.Client(session)

for event in client.bots.stream_incoming_events():
    if event['type'] == 'challenge':
        client.bots.accept_challenge(event['challenge']['id'])
    if event['type'] == 'gameStart':
        print("game start")
        game = Game(client, event['game']['id'])
        game.start()

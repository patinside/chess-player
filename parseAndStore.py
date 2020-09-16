import chess.pgn
from redisClient import RedisClient

# pgn=open("lichess_db_standard_rated_2013-01.pgn")
# pgn =open("lichess_db_standard_rated_2020-02.pgn")
pgn = open('D:\Saved folder\python\chess-player\lichess_db_standard_rated_2020-02.pgn')
# pgn=open("test.pgn")

data={}
i=0
client = RedisClient()

while True:
    i += 1
    j = 1
    print("game: "+ str(i))

    game = chess.pgn.read_game(pgn)

    if game is None:
        break

    board = game.board()
    print (board.board_fen())
    for move in game.mainline_moves():
        if (j%2==1):
            player = "white"
            if(game.headers.get("WhiteElo").isdigit()):
                level = int(game.headers.get("WhiteElo"))//100
            elif(game.headers.get("BlackElo").isdigit()):
                level = int(game.headers.get("BlackElo")) // 100
            else:

                level = 0

        else:
            player = "black"
            if (game.headers.get("BlackElo").isdigit()):
                level = int(game.headers.get("BlackElo")) // 100
            elif (game.headers.get("WhiteElo").isdigit()):
                level = int(game.headers.get("WhiteElo")) // 100
            else:
                level = 0

        key = str(chess.polyglot.zobrist_hash(board))
        print(key)
        client.conn.hincrby(key, str(level) + ":" + str(move) + ":" + player, 1)
        board.push(move)
        j+=1



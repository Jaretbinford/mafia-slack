import random
from models.gameState import States as GameStates
from models.player import Player, Roles, States as PlayerStates

class Actions:
    START_GAME = 'START_GAME'
    ACCUSE = 'ACCUSE'
    MURDER = 'MURDER'
    GUILTY = 'GUILTY'
    NOT_GUILTY = 'NOT_GUILTY'

    ADD_PLAYER = 'ADD_PLAYER'
    REMOVE_PLAYER = 'REMOVE_PLAYER'

class GameStateManager(object):
    
    def __init__(self, gameState):
        self.gameState = gameState

    def transition(self, action, data=None, executor=None):
        if self.gameState.state == GameStates.MARSHALLING:
            return self._transitionFromMarshalling(action, data, executor)
        elif self.gameState.state == GameStates.NIGHT:
            return self._transitionFromNight(action, data, executor)
        elif self.gameState.state == GameStates.DAY:
            return self._transitionFromDay(action, data, executor)
        elif self.gameState.state == GameStates.TRIAL:
            return self._transitionFromTrial(action)
    
    def _transitionFromMarshalling(self, action, data, executor):
        if action == Actions.START_GAME:
            if len(self.gameState.players) >= 4:
                self._assignPlayerRoles()
                self.gameState.state = GameStates.NIGHT
                return True
        elif action == Actions.ADD_PLAYER:
            p = Player(data)
            if len([p for p in self.gameState.players if p.id == data]) == 0:
                self.gameState.players.append(p)
                return True
        elif action == Actions.REMOVE_PLAYER:
            toRemove = self._findPlayerWithId(data)
            self.gameState.players.remove(toRemove)
            return True
        return False

    def _transitionFromNight(self, action, data, executor):
        if action == Actions.MURDER:
            toMurder = self._findPlayerWithId(data)
            murderer = self._findPlayerWithId(executor)
            murderer.vote = toMurder.id
            mafiaMembers = self._findPlayersWithRole(Roles.MAFIA)
            if len([m for m in mafiaMembers if m.vote == toMurder.id]) == len([m for m in mafiaMembers if m.state == PlayerStates.ALIVE]):
                toMurder.state = PlayerStates.DEAD
                if self._isGameOver():
                    self.gameState.state = GameStates.GAME_OVER
                    return True
                else:
                    self.gameState.state = GameStates.DAY
                    return True

    def _transitionFromDay(self, action, data, executor):
        if action == Actions.ACCUSE:
            accusedPlayer = self._findPlayerWithId(data)
            accusedPlayer.state = PlayerStates.ON_TRIAL
            self.gameState.state = GameStates.TRIAL

    def _transitionFromTrial(self, action):
        player = self._findPlayersWithState(PlayerStates.ON_TRIAL)[0]
        if action == Actions.NOT_GUILTY:
            player.state = PlayerStates.ALIVE
            self.gameState.state = GameStates.DAY
        elif action == Actions.GUILTY:
            player.state = PlayerStates.DEAD
            if self._isGameOver():
                self.gameState.state = GameStates.GAME_OVER
            else:
                self.gameState.state = GameStates.NIGHT

    def _assignPlayerRoles(self):
        numMafia = self._getMafiaCount()
        shuffledRoster = random.sample(self.gameState.players,len(self.gameState.players))
        for p in shuffledRoster[:numMafia]:
            p.role = Roles.MAFIA
        for p in shuffledRoster[numMafia:]:
            p.role = Roles.VILLAGER
    
    def _getMafiaCount(self):
        return len(self.gameState.players) // 3

    def _findPlayerWithId(self, id):
        return [p for p in self.gameState.players if p.id == id][0]
    
    def _findPlayersWithState(self, state):
        return [p for p in self.gameState.players if p.state == state]
    def _findPlayersWithRole(self, role):
        return [p for p in self.gameState.players if p.role == role]

    def _isGameOver(self):
        mafiaCount = len([p for p in self.gameState.players if p.role == Roles.MAFIA and p.state == PlayerStates.ALIVE])
        villagerCount = len([p for p in self.gameState.players if p.role == Roles.VILLAGER and p.state == PlayerStates.ALIVE])
        
        return mafiaCount == 0 or villagerCount == mafiaCount

    def printGameState(self):
        playerList = sorted(self.gameState.players,key=lambda player: player.role)
        print('ROSTER:')
        print('id|role|state')
        for p in playerList:
            print(p)
        print(f'GAME STATE: {self.gameState.state}')
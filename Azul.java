package comp1110.ass2;

import java.util.HashSet;
import java.util.Random;

public class Azul {
    /**
     * Given a shared state string, determine if it is well-formed.
     * Note: you don't need to consider validity for this task.
     * A sharedState is well-formed if it satisfies the following conditions.
     * <p>
     * <p>
     * [turn][factories][centre][bag][discard]
     * <p>
     * where [turn][factories], [centre], [bag] and [discard] are replaced by the
     * corresponding small string as described below.
     * <p>
     * 0. [turn] The Turn substring is one character 'A'-'D' representing a
     * player, which indicates that it is this player's turn to make the next
     * drafting move. (In a two-player game, the turn substring can only take
     * the values 'A' or 'B').
     * <p>
     * 1. [factories] The factories substring begins with an 'F'
     * and is followed by a collection of *up to* 5 5-character factory strings
     * representing each factory.
     * Each factory string is defined in the following way:
     * 1st character is a sequential digit '0' to '4' - representing the
     * factory number.
     * 2nd - 5th characters are 'a' to 'e', alphabetically - representing
     * the tiles.
     * A factory may have between 0 and 4 tiles. If a factory has 0 tiles,
     * it does not appear in the factories string.
     * Factory strings are ordered by factory number.
     * For example: given the string "F1aabc2abbb4ddee": Factory 1 has tiles
     * 'aabc', Factory 2 has tiles 'abbb', Factory 4 has tiles 'ddee', and
     * Factories 0 and 4 are empty.
     * <p>
     * 2. [centre] The centre substring starts with a 'C'
     * This is followed by *up to* 15 characters.
     * Each character is 'a' to 'e', alphabetically - representing a tile
     * in the centre.
     * The centre string is sorted alphabetically.
     * For example: "Caaabcdde" The Centre contains three 'a' tiles, one 'b'
     * tile, one 'c' tile, two 'd' tile and one 'e' tile.
     * <p>
     * 3. [bag] The bag substring starts with a 'B'
     * and is followed by 5 2-character substrings
     * 1st substring represents the number of 'a' tiles, from 0 - 20.
     * 2nd substring represents the number of 'b' tiles, from 0 - 20.
     * 3rd substring represents the number of 'c' tiles, from 0 - 20.
     * 4th substring represents the number of 'd' tiles, from 0 - 20.
     * 5th substring represents the number of 'e' tiles, from 0 - 20.
     * <p>
     * For example: "B0005201020" The bag contains zero 'a' tiles, five 'b'
     * tiles, twenty 'c' tiles, ten 'd' tiles and twenty 'e' tiles.
     * 4. [discard] The discard substring starts with a 'D'
     * and is followed by 5 2-character substrings defined the same as the
     * bag substring.
     * For example: "D0005201020" The bag contains zero 'a' tiles, five 'b'
     * tiles, twenty 'c' tiles, ten 'd' tiles, and twenty 'e' tiles.
     *
     * @param sharedState the shared state - factories, bag and discard.
     * @return true if sharedState is well-formed, otherwise return false
     * TASK 2
     */
    public static boolean isSharedStateWellFormed(String sharedState) {
        // FIXME Task 2
        String turns = "ABCD";
        int len = sharedState.length();
        if (!turns.contains(sharedState.substring(0, 1))) {
            return false;
        }
        if (sharedState.charAt(1) != 'F') {
            return false;
        }
        int CIndex = 0;
        int BIndex = 0;
        int DIndex = 0;
        for (int i = 0; i < len; i++) {
            if (sharedState.charAt(i) == 'C') {
                CIndex = i;
            }
            if (sharedState.charAt(i) == 'B') {
                BIndex = i;
            }
            if (sharedState.charAt(i) == 'D') {
                DIndex = i;
            }
        }
        if (!isFactoryWellFormed(sharedState.substring(2, CIndex))) {
            return false;
        }
        if (BIndex - CIndex > 1 && !isSorted(sharedState.substring(CIndex + 1, BIndex))) {
            return false;
        }
        if (!isBagWellFormed(sharedState.substring(BIndex + 1, DIndex)) || !isBagWellFormed(sharedState.substring(DIndex + 1, len))) {
            return false;
        }

        return true;
    }


    public static boolean isFactoryWellFormed(String factory) {
        int number = -1;
        int index = -5;
        int i = 0;
        while (i < factory.length()) {
            if (i == factory.length() - 1 && i - index != 4) {
                return false;
            }
            if (Character.isDigit(factory.charAt(i))) {
                if (i - index != 5) {
                    return false;
                }
                index = i;
                if ((int) factory.charAt(i) < number) {
                    return false;
                } else {
                    number = (int) factory.charAt(i);
                }
                if (!isSorted(factory.substring(i, i + 4))) {
                    return false;
                }
            }
            i++;
        }
        return true;
    }

    public static boolean isSorted(String str) {
        char start = str.charAt(0);
        for (int i = 1; i < str.length(); i++) {
            if (str.charAt(i) < start) {
                return false;
            }
            start = str.charAt(i);
        }
        return true;
    }

    public static boolean isBagWellFormed(String bag) {
        if (bag.length() != 10) {
            return false;
        }
        for (int i = 0; i < 5; i++) {
            if (Integer.parseInt(bag.substring(i * 2, i * 2 + 2)) < 0 || Integer.parseInt(bag.substring(i * 2, i * 2 + 2)) > 20) {
                return false;
            }

        }
        return true;
    }


    /**
     * Given a playerState, determine if it is well-formed.
     * Note: you don't have to consider validity for this task.
     * A playerState is composed of individual playerStrings.
     * A playerState is well-formed if it satisfies the following conditions.
     * <p>
     * A playerString follows this pattern: [player][score][mosaic][storage][floor]
     * where [player], [score], [mosaic], [storage] and [floor] are replaced by
     * a corresponding substring as described below.
     * Each playerString is sorted by Player i.e. Player A appears before Player B.
     * <p>
     * 1. [player] The player substring is one character 'A' to 'D' -
     * representing the Player
     * <p>
     * 2. [score] The score substring is one or more digits between '0' and '9' -
     * representing the score
     * <p>
     * 3. [mosaic] The Mosaic substring begins with a 'M'
     * Which is followed by *up to* 25 3-character strings.
     * Each 3-character string is defined as follows:
     * 1st character is 'a' to 'e' - representing the tile colour.
     * 2nd character is '0' to '4' - representing the row.
     * 3rd character is '0' to '4' - representing the column.
     * The Mosaic substring is ordered first by row, then by column.
     * That is, "a01" comes before "a10".
     * <p>
     * 4. [storage] The Storage substring begins with an 'S'
     * and is followed by *up to* 5 3-character strings.
     * Each 3-character string is defined as follows:
     * 1st character is '0' to '4' - representing the row - each row number must only appear once.
     * 2nd character is 'a' to 'e' - representing the tile colour.
     * 3rd character is '0' to '5' - representing the number of tiles stored in that row.
     * Each 3-character string is ordered by row number.
     * <p>
     * 5. [floor] The Floor substring begins with an 'F'
     * and is followed by *up to* 7 characters in alphabetical order.
     * Each character is 'a' to 'f' - where 'f' represents the first player token.
     * There is only one first player token.
     * <p>
     * An entire playerState for 2 players might look like this:
     * "A20Ma02a13b00e42S2a13e44a1FaabbeB30Mc01b11d21S0e12b2F"
     * If we split player A's string into its substrings, we get:
     * [A][20][Ma02a13b00e42][S2a13e44a1][Faabbe].
     *
     * @param playerState the player state string
     * @return True if the playerState is well-formed,
     * false if the playerState is not well-formed
     * TASK 3
     */
    public static boolean isPlayerStateWellFormed(String playerState) {
        // FIXME Task 3
        String turns = "ABCD";
        int secondPlayerIndex = 0;
        int len = playerState.length();
        for (int i = 1; i < len; i++) {
            if (turns.contains(playerState.substring(i, i + 1))) {
                secondPlayerIndex = i;
                break;
            }
        }
        return isSinglePlayerWellFormed(playerState.substring(0, secondPlayerIndex)) && isSinglePlayerWellFormed(playerState.substring(secondPlayerIndex, len));

    }

    public static boolean isSinglePlayerWellFormed(String singlePlayer) {
        String turns = "ABCD";
        int len = singlePlayer.length();
        if (!turns.contains(singlePlayer.substring(0, 1))) {
            return false;
        }

        int MIndex = 0;
        int SIndex = 0;
        int FIndex = 0;
        for (int i = 0; i < len; i++) {
            if (singlePlayer.charAt(i) == 'M') {
                MIndex = i;
            }
            if (singlePlayer.charAt(i) == 'S') {
                SIndex = i;
            }
            if (singlePlayer.charAt(i) == 'F') {
                FIndex = i;
            }
        }
        if (MIndex == 0 || SIndex == 0 || FIndex == 0) {
            return false;
        }
        if (!isScoreWellFormed(singlePlayer.substring(1, MIndex))) {
            return false;
        }
        if (!isMosaicWellFormed(singlePlayer.substring(MIndex + 1, SIndex))) {
            return false;
        }
        if (!isStorageWellFormed(singlePlayer.substring(SIndex + 1, FIndex))) {
            return false;
        }
        if (!isFloorWellFormed(singlePlayer.substring(FIndex + 1, len))) {
            return false;
        }
        return true;
    }

    public static boolean isScoreWellFormed(String score) {
        for (int i = 0; i < score.length(); i++) {
            if (!Character.isDigit(score.charAt(i))) {
                return false;

            }
        }
        return true;
    }

    public static boolean isMosaicWellFormed(String mosaic) {
        int len = mosaic.length();
        if (len > 75) {
            return false;
        }
        int lastIndex = -3;
        int i = 0;
        while (i < len) {
            if (i == len - 1 && i - lastIndex != 2) {
                return false;
            }
            if (Character.isAlphabetic(mosaic.charAt(i))) {
                if (i - lastIndex != 3) {
                    return false;
                }
                lastIndex = i;
            }
            i++;
        }
        return true;
    }

    public static boolean isStorageWellFormed(String storage) {
        int len = storage.length();
        if (len > 15) {
            return false;
        }
        int lastIndex = -2;
        int i = 0;
        while (i < len) {
            if (Character.isAlphabetic(storage.charAt(i))) {

                if (i - lastIndex != 3) {
                    return false;
                }
                lastIndex = i;
            }
            i++;
        }
        return true;
    }

    public static boolean isFloorWellFormed(String floor) {
        int len = floor.length();
        if (len > 7) {
            return false;
        }
        String tiles = "abcdef";
        int fFreq = 0;
        for (int i = 0; i < len; i++) {
            if (!tiles.contains(floor.substring(i, i + 1))) {
                return false;
            }
            if (floor.charAt(i) == 'f') {
                fFreq++;
            }
        }
        if (fFreq > 1) {
            return false;
        }
        return true;
    }


    /**
     * Given the gameState, draw a *random* tile from the bag.
     * If the bag is empty, refill the the bag with the discard pile and then draw a tile.
     * If the discard pile is also empty, return 'Z'.
     *
     * @param gameState the current game state
     * @return the tile drawn from the bag, or 'Z' if the bag and discard pile are empty.
     * TASK 5
     */
    public static char drawTileFromBag(String[] gameState) {
        // FIXME Task 5
        String sharedState = gameState[0];
        int len = sharedState.length();
        int BIndex = 0;
        int DIndex = 0;
        for (int i = 1; i < len; i++) {
            if (sharedState.charAt(i) == 'B') {
                BIndex = i;
            }
            if (sharedState.charAt(i) == 'D') {
                DIndex = i;
            }
        }
        String bag = sharedState.substring(BIndex + 1, DIndex);
        String discard = sharedState.substring(DIndex + 1, len);
        if (isEmpty(bag) && isEmpty(discard)) {
            return 'Z';
        }
        if (isEmpty(bag) && !isEmpty(discard)) {
            bag=discard;
            gameState[0]=swapBagAndDiscard(sharedState,BIndex,DIndex,len);
        }
        int[] arr=new int[5];
        for(int i=0;i<5;i++){
            arr[i]=Integer.parseInt(bag.substring(i*2,i*2+2));
        }
        for(int i=1;i<5;i++){
            arr[i]=arr[i]+arr[i-1];
        }
        Random rand=new Random();
        int random= rand.nextInt(arr[4]-1+1)+1;
        int type=-1;
        char[] types={'a','b','c','d','e'};
        for(int i=0;i<5;i++){
            if(arr[i]>=random){
                type=i;
                break;
            }
        }
        return types[type];
    }

    public static boolean isEmpty(String str){
        for(int i=0;i<str.length();i++){
            if(str.charAt(i)!='0'){
                return false;
            }
        }
        return true;
    }
    public static String swapBagAndDiscard(String str,int BIndex,int DIndex,int len){
        String res="";
        res+=str.substring(0,BIndex+1);
        res+=str.substring(DIndex+1,len);
        res+="D0000000000";
        return res;
    }

    public static void main(String[] args) {
        String[] state = {"AFCB0000000000D1113080909", "A5Me00c01d02a04d10b14a20b21c23e32d43S0b11c22e33a34c3FeeeB11Me00b01d03a04d10e11a13d21b23a30e32a42S1b22c23d44c3Fdf"};
        drawTileFromBag(state);
    }
    /**
     * Given a state, refill the factories with tiles.
     * If the factories are not all empty, return the given state.
     *
     * @param gameState the state of the game.
     * @return the updated state after the factories have been filled or
     * the given state if not all factories are empty.
     * TASK 6
     */
    public static String[] refillFactories(String[] gameState) {
        // FIXME Task 6
        return null;
    }

    /**
     * Given a gameState for a completed game,
     * return bonus points for rows, columns, and sets.
     *
     * @param gameState a completed game state
     * @param player    the player for whom the score is to be returned
     * @return the number of bonus points awarded to this player for rows,
     * columns, and sets
     * TASK 7
     */
    public static int getBonusPoints(String[] gameState, char player) {
        // FIXME Task 7
        return -1;
    }

    /**
     * Given a valid gameState prepare for the next round.
     * 1. Empty the floor area for each player and adjust their score accordingly (see the README).
     * 2. Refill the factories from the bag.
     * * If the bag is empty, refill the bag from the discard pile and then
     * (continue to) refill the factories.
     * * If the bag and discard pile do not contain enough tiles to fill all
     * the factories, fill as many as possible.
     * * If the factories and centre contain tiles other than the first player
     * token, return the current state.
     *
     * @param gameState the game state
     * @return the state for the next round.
     * TASK 8
     */
    public static String[] nextRound(String[] gameState) {
        // FIXME TASK 8
        return null;
    }

    /**
     * Given an entire game State, determine whether the state is valid.
     * A game state is valid if it satisfies the following conditions.
     * <p>
     * [General]
     * 1. The game state is well-formed.
     * 2. There are no more than 20 of each colour of tile across all player
     * areas, factories, bag and discard
     * 3. Exactly one first player token 'f' must be present across all player
     * boards and the centre.
     * <p>
     * [Mosaic]
     * 1. No two tiles occupy the same location on a single player's mosaic.
     * 2. Each row contains only 1 of each colour of tile.
     * 3. Each column contains only 1 of each colour of tile.
     * [Storage]
     * 1. The maximum number of tiles stored in a row must not exceed (row_number + 1).
     * 2. The colour of tile stored in a row must not be the same as a colour
     * already found in the corresponding row of the mosaic.
     * <p>
     * [Floor]
     * 1. There are no more than 7 tiles on a single player's floor.
     * [Centre]
     * 1. The number of tiles in the centre is no greater than 3 * the number of empty factories.
     * [Factories]
     * 1. At most one factory has less than 4, but greater than 0 tiles.
     * Any factories with factory number greater than this factory must contain 0 tiles.
     *
     * @param gameState array of strings representing the game state.
     *                  state[0] = sharedState
     *                  state[1] = playerStates
     * @return true if the state is valid, false if it is invalid.
     * TASK 9
     */
    public static boolean isStateValid(String[] gameState) {
        // FIXME Task 9
        return false;
    }

    /**
     * Given a valid gameState and a move, determine whether the move is valid.
     * A Drafting move is a 4-character String.
     * A Drafting move is valid if it satisfies the following conditions:
     * <p>
     * 1. The specified factory/centre contains at least one tile of the specified colour.
     * 2. The storage row the tile is being placed in does not already contain a different colour.
     * 3. The corresponding mosaic row does not already contain a tile of that colour.
     * Note that the tile may be placed on the floor.
     * </p>
     * <p>
     * A Tiling move is a 3-character String.
     * A Tiling move is valid if it satisfies the following conditions:
     * 1. The specified row in the Storage area is full.
     * 2. The specified column does not already contain a tile of the same colour.
     * 3. The specified location in the mosaic is empty.
     * 4. If the specified column is 'F', no valid move exists from the
     * specified row into the mosaic.
     * </p>
     *
     * @param gameState the game state.
     * @param move      A string representing a move.
     * @return true if the move is valid, false if it is invalid.
     * TASK 10
     */
    public static boolean isMoveValid(String[] gameState, String move) {
        // FIXME Task 10
        return false;
    }

    /**
     * Given a gameState and a move, apply the move to the gameState.
     * If the move is a Tiling move, you must also update the player's score.
     * If the move is a Tiling move, you must also empty the remaining tiles
     * into the discard.
     * If the move is a Drafting move, you must also move any remaining tiles
     * from the specified factory into the centre.
     * If the move is a Drafting move and you must put tiles onto the floor,
     * any tiles that cannot fit on the floor are placed in the discard with
     * the following exception:
     * If the first player tile would be placed into the discard, it is instead
     * swapped with the last tile in the floor, when the floor is sorted
     * alphabetically.
     *
     * @param gameState the game state.
     * @param move      A string representing a move.
     * @return the updated gameState after the move has been applied.
     * TASK 11
     */
    public static String[] applyMove(String[] gameState, String move) {
        // FIXME Task 11
        return null;
    }

    /**
     * Given a valid game state, return a valid move.
     *
     * @param gameState the game state
     * @return a move for the current game state.
     * TASK 13
     */
    public static String generateAction(String[] gameState) {
        // FIXME Task 13
        return null;
        // FIXME Task 15 Implement a "smart" generateAction()
    }
}

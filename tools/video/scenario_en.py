# English scenario. Same scenes and actions as scenario.py; button and table names are taken from TX.en in docs/index.html.
SCENES = [
 ("intro", [
  ("Hello! This is a trainer for badminton doubles. It shows a pair how to move on the court.", None),
  ("You see the court from above: Blue at the bottom, Red at the top. After every shot you see who takes the shuttle and where both players should stand.", "intro_court"),
 ]),
 ("tabs", [
  ("At the top right there are four tabs: Play, Lessons, Quiz and Help.", "tabs_hover"),
  ("Next to them is the language switch: you can choose Russian, English or Indonesian.", "lang_switch"),
 ]),
 ("table", [
  ("Right now the Red player with the shuttle is hitting, and Blue are waiting. The card tells you what is going on.", "to_card"),
  ("Below is the table called “Most likely course of play”. It lists every shot the hitter can play and how often it is played.", "table_cols"),
  ("The last column shows which Blue player takes the shuttle. The coloured dot shows whether the defence gets there: green, yellow or red.", "table_dots"),
  ("Point the mouse at a row, and the path of the shuttle lights up on the court.", "table_hover"),
 ]),
 ("ways", [
  ("You can play a shot in three ways. First: click a row of the table.", "way_row"),
  ("Second: click the dot at the end of a line right on the court.", "way_dot"),
  ("Third: take the big shuttle at the hitter and drag it anywhere on the opponent’s half.", "way_drag"),
  ("The shot type is chosen for you by where you let go of the shuttle: the farther from the net, the longer the shot.", "way_drag2"),
 ]),
 ("types", [
  ("Above the court you can pick the shot type. Let’s choose “Clear”: the hitter’s partner steps back, because after this shot the pair defends.", "type_clear"),
  ("Now choose “Smash” and drag the shuttle right up to the net. A red cross appears with the words “Smash won’t reach there”.", "type_smash_bad"),
  ("If you let go here, nothing happens. Pick another spot, and the smash is played. The “Auto” button brings back the usual choice.", "type_smash_ok"),
 ]),
 ("auto", [
  ("The “Auto rally” button under the court plays by itself: shots are picked at random, the common and dangerous ones more often.", "auto_on"),
  ("“Pause” freezes the picture at any moment, even while the shuttle is flying. While paused, click a table row, and that is the next shot.", "pause_pick"),
 ]),
 ("player", [
  ("You can move the players. Drag the player who is waiting for the shot, and the partner steps to the best spot by themselves.", "drag_player"),
  ("The dashed circle shows the best place for a player. And the “Best positions” button puts both players there for you.", "relax"),
 ]),
 ("tips", [
  ("Press “Tips”, and the app will rate how you placed the player.", "tips_on"),
  ("Let’s put the player right at the net when the hit comes from above. The “Wrong” window explains why that does not work.", "tip_bad"),
  ("And if you put the player on the best spot, you get “Correct”.", "tip_good"),
 ]),
 ("history", [
  ("Play any shot and press “Back”: you go back one shot. And “Start over” begins the rally again.", "back_reset"),
 ]),
 ("tabs2", [
  ("The “Lessons” tab has short step-by-step explanations.", "show_lessons"),
  ("The “Quiz” tab has a hundred tasks. Place the players and press “Check”. The grid of numbers shows which tests you have already done.", "show_quiz"),
  ("And the “Help” tab has the basics of the game and answers to common questions.", "show_help"),
 ]),
 ("end", [
  ("That’s all. Open the Play tab, drag the shuttle, and see how the pair moves. Good luck on the court!", "finish"),
 ]),
]

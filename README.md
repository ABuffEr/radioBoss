# RadioBOSS NVDA add-on

This add-on provides various enhancements for RadioBOSS by [DJSoft.Net.][1]

Majority of features requires you have enabled Remote API in RadioBOSS settings, and filled add-on settings accordingly.

## Note about labels

This add-on integrates the labelAutofinder module, that associates text labels with edit and combo boxes automagically.

For some obscure reason, if you restart NVDA with, e.g., Music Library opened, labels disappear completely.

Minimize from alt+space menu and then return to window with alt+tab to fix it.

## Gestures

All gestures are customizable under Input Gestures dialog of NVDA, in RadioBOSS section.

Some ones are global (available even without the app in foreground), some others not (just in the app).

### Assigned gestures

* F8: enables/disables microphone, and reports it (app only)(*);

(*): this gesture must be manually aligned with one configured in RadioBOSS.

### Not assigned gestures

Globals:

* reports detail (artist, title, album...) of the current track (each detail can have a gesture);
* reports elapsed time of the current track;
* reports remaining time of the current track;
* reports remaining time of the playlist;
* views in a dialog all details of the current track.

App only:

* reports detail (artist, title, album...) of the track at focused position in the playlist (each detail can have a gesture);
* views in a dialog all details of the track at focused position in the playlist;

## Warning

Notice that, to work correctly, the last two gestures require you have enabled at least the # column in playlist treeview (the column with position). All other columns can be hidden, if you want.


[1]: https://www.djsoft.net

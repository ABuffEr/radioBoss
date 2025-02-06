# RadioBOSS NVDA add-on

This add-on provides various enhancements for RadioBOSS by [DJSoft.Net.][1]

Majority of features requires you have enabled Remote API in RadioBOSS settings, and filled add-on settings accordingly.

This add-on integrates the labelAutofinder module, that associates text labels with edit and combo boxes automagically.


## Gestures

All gestures are customizable under Input Gestures dialog of NVDA, in RadioBOSS section.

One gesture is global (available even without the app in foreground), the others not (just in the app).

### Assigned gestures

* F8: enables/disables microphone, and reports it (app only)(*);

(*): this gesture must be manually aligned with one configured in RadioBOSS.

### Not assigned gestures

Global:

* switches between RadioBOSS and other windows where you are.

App only:

* reports detail (artist, title, album...) of the current track (each detail can have a gesture);
* reports detail (artist, title, album...) of the track at focused position in the playlist (each detail can have a gesture);
* reports elapsed time of the current track;
* reports remaining time of the current track;
* reports remaining time of the playlist;
* views in a dialog all details of the current track;
* views in a dialog all details of the track at focused position in the playlist.

## Warning

Notice that, to work correctly, gestures based on track at focused position require you have enabled at least the # column in playlist treeview (the column with position). All other columns can be hidden, if you want.


[1]: https://www.djsoft.net

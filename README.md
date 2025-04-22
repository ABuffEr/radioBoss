# RadioBOSS NVDA add-on

This add-on provides various enhancements for RadioBOSS by [DJSoft.Net.][1]

Majority of features requires you have enabled Remote API in RadioBOSS settings, and filled add-on settings accordingly.

This add-on integrates the [labelAutofinderCore][2] module, that improves the sliders and associates labels with edit/combo boxes automagically.


## Gestures

All gestures are customizable under Input Gestures dialog of NVDA, in RadioBOSS sections.

Yes, there are two sections: "RadioBOSS (global)", always available, and "RadioBOSS (app only)", that appears when you open RadioBOSS app.

A lot of gestures are common to both sections.

### Assigned gestures

* F8: enables/disables microphone, and reports it (app only)(*);

(*): this gesture must be manually aligned with one configured in RadioBOSS.

### Not assigned gestures

Global only:

* switches between RadioBOSS and other windows where you are.

App only:

* jumps to log events;
* jumps to playlist tree;
* reports detail (artist, title, album...) of the track at focused position in the playlist (each detail can have a gesture);
* views in a dialog all details of the track at focused position in the playlist.

App & global:

* reports a summary of previous/current/next track info (info can be customized in settings);
* reports detail (artist, title, album...) of the current track (each detail can have a gesture);
* reports elapsed time of the current track;
* reports remaining time of the current track;
* reports remaining time of the playlist;
* views in a dialog all details of the current track.

## Warning

Notice that, to work correctly, gestures based on track at focused position require you have enabled at least the # column in playlist treeview (the column with position). All other columns can be hidden, if you want.


[1]: https://www.djsoft.net
[2]: https://github.com/ABuffEr/labelAutofinderCore

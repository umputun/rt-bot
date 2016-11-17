"use strict";
var AnekdotData = (function () {
    function AnekdotData() {
    }
    AnekdotData.parseFromObject = function (o) {
        var anekdot = new AnekdotData();
        anekdot.guid = o.guid[0];
        anekdot.title = o.title[0];
        anekdot.pubDate = o.pubDate[0];
        anekdot.description = o.description[0];
        anekdot.description = anekdot.description.replace(/<br>/g, "  \\n");
        anekdot.description = anekdot.description.replace(/- /g, "— ");
        return anekdot;
    };
    AnekdotData.getDefaultAnekdot = function () {
        var anekdot = new AnekdotData();
        anekdot.description = "Забыл все анекдоты";
        return anekdot;
    };
    return AnekdotData;
}());
exports.AnekdotData = AnekdotData;

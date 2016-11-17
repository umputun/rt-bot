export class AnekdotData {
    guid: string;
    title: string;
    pubDate: string;
    description: string;

    public static parseFromObject(o: any) {
        var anekdot = new AnekdotData();
        anekdot.guid = o.guid[0];
        anekdot.title = o.title[0];
        anekdot.pubDate = o.pubDate[0];
        anekdot.description = o.description[0];
        anekdot.description = anekdot.description.replace(/<br>/g, "  \\n");
        anekdot.description = anekdot.description.replace(/- /g, "— ");

        return anekdot;
    }

    public static getDefaultAnekdot(): AnekdotData {
        var anekdot = new AnekdotData();
        anekdot.description = "Забыл все анекдоты";
        return anekdot;
    }
}
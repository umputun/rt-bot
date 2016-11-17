import {AnekdotData} from "./AnekdotData";
import {AnekdotLoader} from "./AnekdotLoader";
export class AnekdotChannel {

    private rssUrl: string;
    private tags: string[] = [];
    private anekdots: AnekdotData[] = [AnekdotData.getDefaultAnekdot()];
    private index = 0;

    constructor(private loader: AnekdotLoader, rssUrl: string, tags: string[]) {
        this.load(rssUrl, tags);
    }

    public getTags(): string[] {
        return this.tags;
    }

    public getAnekdot(): AnekdotData {
        if (this.index >= this.anekdots.length) {
            this.index = 0;
        }
        var anekdot = this.anekdots[this.index];
        this.index++;
        return anekdot;
    }

    private load(rssUrl: string, tags: string[]) {
        this.rssUrl = rssUrl;
        this.tags = tags;
        this.loader.on('error', this.onLoadError.bind(this));
        this.loader.on('complete', this.onLoadComplete.bind(this));
        this.loader.load(rssUrl);
    }

    private onLoadError(error, url) {
        console.log(`Error while loading ${url}. Details: ${error}`);
    }

    private onLoadComplete(url: string, anekdots: AnekdotData[]) {
        if (url != this.rssUrl) {
            return;
        }
        console.log(`Anekdots loaded. URL: ${url} Tags: ${this.tags}`);
        this.anekdots = anekdots;
        this.index = 0;
    }
}
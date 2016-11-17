export class RequestData {
    public text: string;
    public username: string;
    public display_name: string;

    private static fields = ['text', 'username', 'display_name'];

    public static parseFromObject(data: any): RequestData {
        for (var field of RequestData.fields) {
            if (!data[field]) {
                throw `Error. required field ${field} not set`;
            }
        }

        var requestData = new RequestData();
        for (var field of RequestData.fields) {
            requestData[field] = data[field];
        }

        return requestData;
    }
}
import * as functions from 'firebase-functions';
import * as request from 'request';

// // Start writing Firebase Functions
// // https://firebase.google.com/docs/functions/typescript
//
// export const helloWorld = functions.https.onRequest((request, response) => {
//  response.send("Hello from Firebase!");
// });
exports.refreshContributeProducts = functions.firestore
.document('fl_content/{documentId}')
.onWrite((change, context) => {
    const document = change.after.exists ? change.after.data() : null;
    if(document && document._fl_meta_.schema === 'supportProducts') {
        request.get('https://psyclonicstudios.com.au/refresh_contribute_products')
        return 0;
    } else {
        return 1;
    }
})

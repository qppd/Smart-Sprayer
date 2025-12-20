#ifndef GSM_RECIPIENTS_H
#define GSM_RECIPIENTS_H

#define MAX_RECIPIENTS 10

// SMS Recipients - Add your phone numbers here
String recipients[MAX_RECIPIENTS] = {
    "",  // Recipient 1
    "",  // Recipient 2
    "",  // Recipient 3
    "",  // Recipient 4
    "",  // Recipient 5
    "",  // Recipient 6
    "",  // Recipient 7
    "",  // Recipient 8
    "",  // Recipient 9
    ""   // Recipient 10
};

// Number of active recipients (change this value based on how many you want to use)
int numRecipients = 0;

#endif // GSM_RECIPIENTS_H
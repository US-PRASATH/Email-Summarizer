// src/components/EmailSummary.js
import React from 'react';

const EmailSummary = ({ email, onMarkAsRead }) => {
    return (
        <div
            className={`email-summary p-4 border border-gray-300 rounded-lg shadow-md mb-4 break-words ${
                email.isRead ? 'bg-gray-200' : 'bg-white'
            }`}
        >   
            <h3 className={`text-lg font-semibold ${email.isRead ? 'text-gray-500' : ''}`}>
                Snippet: {email.Snippet}
            </h3>
            <h3 className="text-lg font-semibold mt-2">Subject: {email.Subject}</h3>
            <p className="mt-2">
                <strong className="font-semibold">From:</strong> {email.Sender}
            </p>
            <p className="mt-1">
                <strong className="font-semibold">Date:</strong> {email.Date}
            </p>
            <p className="mt-2">
                <strong className="font-semibold"></strong> {email.Summary}
            </p>
            {!email.isRead && (
                <button
                    onClick={() => onMarkAsRead(email.ID)}
                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    Mark as Read
                </button>
            )}
        </div>
    );
};

export default EmailSummary;

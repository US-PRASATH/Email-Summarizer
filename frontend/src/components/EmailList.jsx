// src/components/EmailList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import EmailSummary from './EmailSummary';
import InfiniteScroll from 'react-infinite-scroll-component';

const EmailList = () => {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [login, setLogin] = useState(false);

    useEffect(() => {
        const fetchEmails = async () => {
            try {
                const response = await axios.get('http://localhost:5000/emails');
                console.log(response.data);
                if (Array.isArray(response.data.emails)) {
                    // Add isRead property to each email initially set to false
                    const emailsWithReadStatus = response.data.emails.map(email => ({
                        ...email,
                        isRead: false,
                    }));
                    setEmails(emailsWithReadStatus);
                } else {
                    setError('Unexpected response format. Expected an array.');
                }
            } catch (err) {
                console.error("Error fetching emails:", err);
                setError('Error fetching emails.');
            } finally {
                setLoading(false);
            }
        };
        
        fetchEmails();
    }, []);
    //window.onload = authenticate;

    const fetchEmails = async () => {
        console.log("next");
        try {
            const response = await axios.get('http://localhost:5000/emails');
            if (Array.isArray(response.data.emails)) {
                // Add isRead property to each email initially set to false
                const emailsWithReadStatus = response.data.emails.map(email => ({
                    ...email,
                    isRead: false,
                }));
                setEmails(emailsWithReadStatus);
            } else {
                setError('Unexpected response format. Expected an array.');
            }
        } catch (err) {
            console.error("Error fetching emails:", err);
            setError('Error fetching emails.');
        } finally {
            setLoading(false);
        }
    };

    // Function to handle marking an email as read
    const markAsRead = (id) => {
        axios.post('http://localhost:5000/mark_as_read/'+id)
        setEmails(emails.map(email =>
            email.ID === id ? { ...email, isRead: true } : email
        ));
    };

    if (loading) {
        return <p className="text-center text-lg font-semibold">Loading...</p>;
    }

    if (error) {
        return <p className="text-center text-lg font-semibold text-red-500">{error}</p>;
    }

    return (
        <div className="email-list container mx-auto px-4">
             <div className="flex justify-center mt-4 mb-5">
                <button 
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    onClick={() => window.location.reload()}
                >
                    Refresh Page
                </button>
            </div>
            {/*<InfiniteScroll dataLength={emails.length} next={fetchEmails} hasMore={true}>*/}
            {emails.length > 0 ? (
                emails.map((email) => (
                    <EmailSummary key={email.ID} email={email} onMarkAsRead={markAsRead} />
                ))
            ) : (
                <p className="text-center text-lg font-semibold">No emails found.</p>
            )}
            {/*</InfiniteScroll>*/}
        </div>
    );
};

export default EmailList;

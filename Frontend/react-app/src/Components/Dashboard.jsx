import React from 'react'
import './Dashboard.css'
import { useState,useRef } from 'react'
import axios from 'axios'
import {marked} from 'marked'
import { useEffect } from 'react'
import cloudArmeeLogo from '../assets/CloudArmeeLogo3.png'
import cloudLogoOnly from '../assets/cloudarmeeLogoOnly.jpg'
import {v4 as uuidv4} from 'uuid'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars, faTimes } from '@fortawesome/free-solid-svg-icons'; // Import faBars and faTimes

const Dashboard = () => {

    const [youtubeURL, setYoutubeURL] = useState('');
    const [loadingText, setLoadingText] = useState("Get YouTube link's blog.....");
    const [showChat, setShowChat] = useState(false);
    const [messages, setMessages] = useState([]);
    const [placeholder, setPlaceholder] = useState('Paste YouTube link here...');
    const [userInput, setUserInput] = useState('');
    const chatEndRef = useRef(null);
    const [historyList, setHistoryList] = useState([])
    const [chatID, setChatID] = useState(null)
    const [showSidebar, setShowSidebar] = useState(false); // New state for sidebar visibility


const handleUserReply = async () => {
    if (!userInput.trim()) return;

    const newUserMessage = { sender: 'user', content: userInput };
    const newMessages = [...messages, newUserMessage];

    setMessages(newMessages);

    // If we haven't processed a URL yet, treat this as the URL input
    if (!youtubeURL) {
        const url = userInput.trim();
        const newChatID = uuidv4();

        setChatID(newChatID)
        setYoutubeURL(url);
        setUserInput('');
        setMessages([
                ...newMessages,
                { sender: 'bot', content: 'Thinking...' },
            ]);

        try {
            const response = await axios.post('http://localhost:5000/process', { youtubeURL: url,
                id:chatID
             });
            const data = response.data;

            const blogContent = {
                sender: 'bot',
                content: marked.parse(data.result),
                isMarkdown: true,
            };
            const followUp = {
                sender: 'bot',
                content: 'Are we good with the content? (yes/no)',
            };

            setMessages([...newMessages, blogContent, followUp]);
            setShowChat(true);
            setPlaceholder('Type "yes" to confirm or "no" to improve...');
        } catch (error) {
            console.error('Axios error:', error);
            const errorMessage = {
                sender: 'bot',
                content: 'Something went wrong while fetching blog content.',
            };
            setMessages([...newMessages, errorMessage]);
            setShowChat(true);
        }
    } else if (userInput.toLowerCase() === 'yes') {
        const finalMessages = [...newMessages, { sender: 'bot', content: 'Awesome! Your blog is finalized.' }];
        setMessages(finalMessages);    
        setUserInput('');
        console.log(finalMessages,chatID,youtubeURL)
        try{
            axios.post(`http://localhost:5000/save`,{
                id: chatID,
                url: youtubeURL,
                chatMessages:finalMessages
            })
            .then(response => {
                console.log(response)
                handleFinalizeChat(finalMessages, chatID, youtubeURL);
            })
            .catch(error => console.log(error))
        }
        catch(error){
            console.log(error)
        }
    } else if (userInput.toLowerCase() === 'no') {
        try {
            setUserInput('');

            setMessages([
                ...newMessages,
                { sender: 'bot', content: 'Thinking...' },
            ]);

            const improveRes = await axios.post('http://localhost:5000/regenerate', {
                youtubeURL,
            });

            const improvedData = improveRes.data;

            setMessages([
                ...newMessages,
                {
                    sender: 'bot',
                    content: marked.parse(improvedData.result),
                    isMarkdown: true,
                },
                {
                    sender: 'bot',
                    content: 'Does this version look better? (yes/no)',
                },
            ]);
        } catch (err) {
            setMessages([
                ...newMessages,
                {
                    sender: 'bot',
                    content: 'Something went wrong while improving the content.',
                },
            ]);
            setUserInput('');
        }
    } else {
        setMessages([
            ...newMessages,
            { sender: 'bot', content: 'Please type "yes" to confirm or "no" to improve.' },
        ]);
        setUserInput('');
    }

    setUserInput('');
};

const handleFinalizeChat = async (currentMessages, currentChatID, currentYoutubeURL) => {
        try {
            await axios.post(`http://localhost:5000/save`, {
                id: currentChatID,
                url: currentYoutubeURL,
                chatMessages: currentMessages
            });
            console.log("Chat saved successfully!");

            // Add the current chat to the history list
            setHistoryList(prevHistory => [
                ...prevHistory,
                { id: currentChatID, url: currentYoutubeURL, title: currentYoutubeURL.substring(0, 30) + '...' } // Or a more descriptive title
            ]);

            // Start a new chat
            setYoutubeURL('');
            setMessages([
                { sender: 'bot', content: `Hi!, our AI tool transforms YouTube video captions into a professional, engaging blog post.You get to review the initial draft and can request a second, improved version if needed.` },
                { sender: 'bot', content: 'Please enter your YouTube URL.' },
            ]);
            setPlaceholder('Paste YouTube link here...');
            setChatID(uuidv4());
        } catch (error) {
            console.error("Error saving chat or initiating new chat:", error);
            setMessages(prevMessages => [
                ...prevMessages,
                { sender: 'bot', content: 'There was an issue saving the chat or starting a new one. Please try again.' },
            ]);
        }
    };

// Function to toggle sidebar visibility
const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
};


useEffect(() => {
    setMessages([
        {
            sender: 'bot',
            content: `Hi!, our AI tool transforms YouTube video captions into a professional, 
            engaging LinkedIn post.You get to review the initial draft and can request a second, improved version if needed.`,
        },
        {
            sender: 'bot',
            content: 'Please enter your YouTube URL.',
        },
    ]);
}, []);

const retrieveChatHistory = async (idToRetrieve) => {
        try {
            // First, clear current chat to show loading or new history
            setMessages([{ sender: 'bot', content: 'Loading chat history...' }]);
            setYoutubeURL(''); // Clear previous URL
            setUserInput(''); // Clear user input
            setPlaceholder('Paste YouTube link here...'); // Reset placeholder

            const response = await axios.get(`http://localhost:5000/history/${idToRetrieve}`);
            const { chatMessages, youtubeURL: retrievedUrl } = response.data;

            if (chatMessages && chatMessages.length > 0) {
                setMessages(chatMessages); // Set the messages from history
                setChatID(idToRetrieve); // Set the current chat ID to the retrieved one
                setYoutubeURL(retrievedUrl || ''); // Set the YouTube URL associated with this history
                // You might want to adjust the placeholder or state based on the retrieved chat's last message
                const lastMessage = chatMessages[chatMessages.length - 1];
                if (lastMessage && lastMessage.content.includes('Are we good with the content?')) {
                    setPlaceholder('Type "yes" to confirm or "no" to improve...');
                } else {
                    setPlaceholder('Type your next query or paste a new YouTube link...');
                }
            } else {
                setMessages([{ sender: 'bot', content: 'No chat history found for this ID.' }]);
            }
        } catch (error) {
            console.error('Error retrieving chat history:', error);
            setMessages([{ sender: 'bot', content: 'Failed to retrieve chat history. Please try again.' }]);
        }
    };


useEffect(() => {
    if (chatEndRef.current) {
        chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
}, [messages]);


    return (
        <div>
            <img src={cloudArmeeLogo} alt="Logo" className="cloudarmeeLogo" />


            <div className="MainDiv">
                {/* Sidebar Wrapper and Icon */}
                <div className="side-nav-wrapper">
                    <div className="menu-icon" onClick={toggleSidebar}>
                        <FontAwesomeIcon icon={showSidebar ? faTimes : faBars} />
                    </div>
                    {/* SubDivLeft is now conditionally rendered with 'show' class */}
                    <div className={`SubDivLeft ${showSidebar ? 'show' : ''}`}>
                        <div className="History">
                            <h5>History</h5>
                            <ul id="historyList" >
                                <li></li>
                            </ul>
                        </div>
                        {/* <button className="btn btn-primary">Explore more GPT's</button> */}
                    </div>
                </div>

                <div className="InputAndOutputDiv" style={{ marginLeft: showSidebar ? '365px' : '205px' }}> {/* Adjusted margin */}
                    {/* <div className="OutputLogo">
                        <img src={cloudLogoOnly} className="CloudarmeelogoOnly"/>
                        <h5 className="youtubeLoadinglabel">{loadingText}</h5>
                    </div> */}
                    <div className="SubInput"></div>

                    <div className="OutputChat">
                        <div className={`chat_container`} id="chatContainer">
                            <div id="chatDisplay" className="chat_display">
                                {messages.map((msg, index) => (
                                msg.isMarkdown ? (
                                    <div
                                    key={index}
                                    className={msg.sender === 'user' ? 'user_msg' : 'bot_msg'}
                                    dangerouslySetInnerHTML={{ __html: msg.content }}
                                    />
                                ) : (
                                    <div
                                    key={index}
                                    className={msg.sender === 'user' ? 'user_msg' : 'bot_msg'}
                                    >
                                    {msg.content}
                                    </div>
                                )
                                ))}
                                <div ref={chatEndRef}></div>
                            </div>

                            <div className="get_input_prompt">
                                <input
                                    type="text"
                                    id="userInput"
                                    className="Input_prompt"
                                    placeholder={placeholder}
                                    value={userInput}
                                    onChange={(e) => setUserInput(e.target.value)}
                                />
                                <button className="sendBtn" onClick={()=> handleUserReply()}>Send</button>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard
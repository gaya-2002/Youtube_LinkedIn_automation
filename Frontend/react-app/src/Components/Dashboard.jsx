import React from 'react'
import './Dashboard.css'
import { useState,useRef } from 'react'
import axios from 'axios'
import {marked} from 'marked'
import { useEffect } from 'react'
import cloudArmeeLogo from '../assets/CloudArmeeLogo3.png'
import cloudLogoOnly from '../assets/cloudarmeeLogoOnly.jpg'
import {v4 as uuidv4} from 'uuid'

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
            .then(response => console.log(response))
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



useEffect(() => {
  setMessages([
    {
      sender: 'bot',
      content: 'Hi! Please enter your YouTube URL.',
    },
  ]);
}, []);

useEffect(() => {
  if (chatEndRef.current) {
    chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }
}, [messages]);


    return (
        <div>
            <div className="Navigation_bar">
                <img src={cloudArmeeLogo} alt="Logo" className="cloudarmeeLogo" />
            </div>

            <div  className="MainDiv">

                <div className="SubDivLeft">
                        <div className="Description">
                            <h5>Description</h5>
                            <p>&emsp; When you share a YouTube video link, our system automatically pulls the captions, 
                                turns them into a blog-style summary, and then rewrites that into a professional blog. 
                                You get to review the blog, and if you’re not happy with it, 
                                we run it through a second round of improvement to make it clearer, more engaging,
                                and better suited for your audience. All powered by AI, working quietly in the background &#128522;.</p>
                        </div>
                        <div className="History">
                            <h5>History</h5>
                            <ul id="historyList">{historyList}</ul>
                        </div>
                        <button className="btn btn-primary">Explore more GPT's</button>
                </div>

                <div className="InputAndOutputDiv">
                        <div className="OutputLogo">
                            <img src={cloudLogoOnly} className="CloudarmeelogoOnly"/>
                            <h5 className="youtubeLoadinglabel">{loadingText}</h5>
                        </div>
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

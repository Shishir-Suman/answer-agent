import React from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  id: string
}

interface MessageItemProps {
  message: Message
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`
          max-w-[80%] rounded-xl p-3
          ${isUser 
            ? 'bg-blue-600 text-white rounded-tr-none' 
            : 'bg-gray-100 text-gray-800 rounded-tl-none'}
        `}
      >
        {message.content}
      </div>
    </div>
  )
}

export default MessageItem 
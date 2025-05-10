document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');

    // Lấy URL của Rasa server từ tham số URL hoặc sử dụng mặc định
    const urlParams = new URLSearchParams(window.location.search);
    const rasaServerUrl = urlParams.get('server') || '';
    console.log('Connecting to Rasa server at:', rasaServerUrl);

    // Xử lý khi người dùng nhấn nút Gửi
    sendButton.addEventListener('click', function() {
        sendMessage();
    });

    // Xử lý khi người dùng nhấn Enter
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Hàm gửi tin nhắn
    function sendMessage() {
        const message = userInput.value.trim();
        if (message.length === 0) return;

        // Hiển thị tin nhắn của người dùng
        addMessage(message, 'user');
        
        // Xóa input
        userInput.value = '';
        
        // Hiển thị trạng thái "đang nhập..."
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot';
        typingIndicator.innerHTML = '<div class="message-content">Đang nhập...</div>';
        typingIndicator.id = 'typing-indicator';
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Gửi tin nhắn đến Rasa server
        fetch(`${rasaServerUrl}/api/webhooks/rest/webhook`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': window.location.origin
            },
            mode: 'cors',
            body: JSON.stringify({
                sender: 'user',
                message: message
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            // Xóa trạng thái "đang nhập..."
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Hiển thị phản hồi từ bot
            if (data && data.length > 0) {
                data.forEach(item => {
                    if (item.text) {
                        addMessage(item.text, 'bot');
                    }
                });
            } else {
                addMessage('Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này.', 'bot');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Xóa trạng thái "đang nhập..."
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            addMessage('Xin lỗi, có lỗi xảy ra khi kết nối với server. Vui lòng thử lại sau.', 'bot');
        });
    }

    // Hàm thêm tin nhắn vào khung chat
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        messageElement.innerHTML = `<div class="message-content">${message}</div>`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

// Hàm để đặt câu hỏi từ các gợi ý
function askQuestion(question) {
    const userInput = document.getElementById('user-input');
    userInput.value = question;
    document.getElementById('send-btn').click();
}

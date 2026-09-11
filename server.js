const express = require("express");
const path = require("path");
require("dotenv").config();

const app = express();

const PORT = process.env.PORT || 3000;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = "gemini-2.5-flash";

if (!GEMINI_API_KEY) {
    console.error("❌ Thiếu GEMINI_API_KEY trong file .env");
    process.exit(1);
}

app.use(express.json({ limit: "1mb" }));

// Cho phép truy cập index.html trong thư mục public
app.use(express.static(path.join(__dirname, "public")));


/*
    POST /api/chat

    Browser → Backend → Gemini
*/
app.post("/api/chat", async (req, res) => {

    try {

        const { messages, systemPrompt } = req.body;

        if (!Array.isArray(messages)) {
            return res.status(400).json({
                error: "messages phải là một mảng."
            });
        }

        const contents = messages.map(message => ({
            role:
                message.role === "user"
                    ? "user"
                    : "model",

            parts: [
                {
                    text: String(message.text || "")
                }
            ]
        }));


        const requestBody = {

            system_instruction: {
                parts: [
                    {
                        text:
                            String(
                                systemPrompt ||
                                "Bạn là Cluder AI."
                            )
                    }
                ]
            },

            contents,

            generationConfig: {
                temperature: 0.75,
                topP: 0.95,
                maxOutputTokens: 4096
            }

        };


        const url =
            "https://generativelanguage.googleapis.com/" +
            "v1beta/models/" +
            GEMINI_MODEL +
            ":generateContent?key=" +
            encodeURIComponent(GEMINI_API_KEY);


        const response = await fetch(
            url,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(requestBody)
            }
        );


        const data = await response.json();


        if (!response.ok) {

            console.error(
                "Gemini API:",
                data
            );

            return res.status(response.status).json({
                error:
                    data?.error?.message ||
                    `Gemini API lỗi HTTP ${response.status}.`
            });
        }


        const text =
            data
                ?.candidates?.[0]
                ?.content?.parts
                ?.map(part => part.text || "")
                .join("")
                .trim();


        if (!text) {

            return res.status(500).json({
                error:
                    "Gemini không trả về nội dung."
            });
        }


        res.json({
            text
        });


    } catch (error) {

        console.error(
            "Server error:",
            error
        );

        res.status(500).json({
            error:
                "Lỗi máy chủ: " +
                error.message
        });

    }

});


/*
    Trang chủ
*/

app.get("/", (req, res) => {

    res.sendFile(
        path.join(
            __dirname,
            "public",
            "index.html"
        )
    );

});


app.listen(
    PORT,
    () => {

        console.log(
            `🚀 Cluder AI chạy tại http://localhost:${PORT}`
        );

    }
);

import { NextRequest, NextResponse } from "next/server";
import { OpenAI } from "openai"; // FIXED IMPORT

// Initialize OpenAI client
const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // Uses your API Key from .env.local
});

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json(); // Get user input

    const completion = await client.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "system", content: "You are a trading AI assistant." }, { role: "user", content: message }],
    });

    return NextResponse.json({ reply: completion.choices[0].message.content });

  } catch (error) {
    console.error("OpenAI API Error:", error);
    return NextResponse.json({ error: "Failed to connect to AI" }, { status: 500 });
  }
}

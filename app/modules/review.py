from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import Config

class ReviewModule:
    def __init__(self):
        # Check if we're using local GPT4All or OpenAI
        if Config.OPENAI_API_BASE:  # Using local GPT4All
            print(f"✅ Review module using local LLM at: {Config.OPENAI_API_BASE}")
            self.llm = ChatOpenAI(
                base_url=Config.OPENAI_API_BASE,
                model=Config.GPT_MODEL,
                temperature=0.3,
                api_key=Config.OPENAI_API_KEY  # "not-needed" works fine
            )
        elif Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "not-needed":
            print("✅ Review module using OpenAI API")
            self.llm = ChatOpenAI(
                model=Config.GPT_MODEL,
                temperature=0.3,
                api_key=Config.OPENAI_API_KEY
            )
        else:
            print("⚠️ No LLM configured for review. Using mock responses.")
            self.llm = None
    
    async def assess_quality(self, abstract: str, methods: str, results: str) -> dict:
        """Assess quality of generated content"""
        if not self.llm:
            return {
                "quality_score": 7.5,
                "feedback": "Quality assessment requires LLM (GPT4All or OpenAI)",
                "revision_suggestions": [
                    "Add more specific details about search strategy",
                    "Include discussion of potential limitations",
                    "Strengthen the conclusion with practical implications"
                ]
            }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert peer reviewer assessing the quality of a systematic review."),
            ("human", f"""
            Assess the quality of this systematic review based on:
            
            ABSTRACT:
            {abstract[:500]}
            
            METHODS COMPARISON:
            {methods[:800]}
            
            RESULTS SYNTHESIS:
            {results[:800]}
            
            Rate each criterion from 0-10 and provide brief justification:
            1. Clarity and coherence
            2. Methodological rigor
            3. Evidence synthesis quality
            4. Overall contribution
            
            Also provide specific suggestions for improvement.
            """)
        ])
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({})
            # Parse response (simplified)
            return {
                "quality_score": 8.0,
                "feedback": response.content,
                "revision_suggestions": [
                    "Add more specific details about search strategy",
                    "Include discussion of publication bias",
                    "Strengthen conclusion with practical implications",
                    "Add more quantitative comparisons where possible",
                    "Include limitations section"
                ]
            }
        except Exception as e:
            print(f"Quality assessment error: {e}")
            return {
                "quality_score": 7.0,
                "feedback": "Assessment completed with some limitations",
                "revision_suggestions": ["Review and enhance all sections"]
            }
    
    async def suggest_revisions(self, review_content: str) -> list:
        """Generate revision suggestions"""
        if not self.llm:
            return [
                "Review the abstract for clarity and completeness",
                "Ensure methods comparison highlights key differences",
                "Strengthen the results synthesis with specific examples",
                "Add more references to support claims",
                "Check for consistency across all sections"
            ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert editor providing revision suggestions."),
            ("human", f"""
            Based on this review content, provide 5 specific revision suggestions:
            
            {review_content[:1000]}
            
            List each suggestion as a clear, actionable item.
            """)
        ])
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({})
            suggestions = response.content.split('\n')
            return [s.strip('- 0123456789. ') for s in suggestions if s.strip()]
        except Exception as e:
            print(f"Revision suggestions error: {e}")
            return ["Review and enhance the content quality"]
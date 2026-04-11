#!/usr/bin/env python3
"""
AlphaForgeFX Complete Codebase Analysis - Push to Notion
This script performs deep analysis and pushes findings to Notion database.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Notion API Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
NOTION_API_URL = "https://api.notion.com/v1"

class NotionAnalysisPublisher:
    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def create_analysis_page(self, analysis_data: Dict[str, Any]) -> str:
        """Create a new page in Notion database with analysis"""
        url = f"{NOTION_API_URL}/pages"
        
        # Split children into chunks of 100 (Notion API limit)
        children = self._build_blocks(analysis_data.get("content", []))
        all_children = []
        
        for i in range(0, len(children), 100):
            chunk = children[i:i+100]
            for child in chunk:
                all_children.append(child)
        
        # Create just first 100 blocks in initial request
        payload = {
            "parent": {"page_id": self.database_id},  # Use page_id instead of database_id
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": analysis_data.get("title", "AlphaForgeFX Analysis")[:100]
                            }
                        }
                    ]
                }
            },
            "children": all_children[:100]
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            page_id = response.json()["id"]
            
            # Add remaining blocks to page
            if len(all_children) > 100:
                self._append_blocks_to_page(page_id, all_children[100:])
            
            return page_id
        else:
            print(f"Error creating page: {response.status_code}")
            print(response.text)
            return None
    
    def _append_blocks_to_page(self, page_id: str, blocks: List[Dict]) -> bool:
        """Append blocks to existing page"""
        url = f"{NOTION_API_URL}/blocks/{page_id}/children"
        
        for i in range(0, len(blocks), 100):
            chunk = blocks[i:i+100]
            payload = {"children": chunk}
            
            response = requests.patch(url, json=payload, headers=self.headers)
            if response.status_code != 200:
                print(f"Error appending blocks: {response.status_code}")
                return False
        
        return True
    
    def _build_blocks(self, content: List[Dict]) -> List[Dict]:
        """Convert content to Notion blocks"""
        blocks = []
        for item in content:
            if item["type"] == "heading_1":
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": item["content"]}}],
                        "color": "default"
                    }
                })
            elif item["type"] == "heading_2":
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": item["content"]}}],
                        "color": "default"
                    }
                })
            elif item["type"] == "paragraph":
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": item["content"]}}],
                        "color": "default"
                    }
                })
            elif item["type"] == "bulleted_list":
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": item["content"]}}],
                        "color": "default"
                    }
                })
        return blocks


class CodebaseAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.analysis_results = {}
    
    def analyze_architecture(self) -> Dict:
        """Analyze overall system architecture"""
        return {
            "title": "🏗️ AlphaForgeFX - Complete Architecture & Code Analysis",
            "type": "Architecture",
            "content": self._generate_architecture_content()
        }
    
    def _generate_architecture_content(self) -> List[Dict]:
        """Generate architecture analysis content"""
        content = [
            {"type": "heading_1", "content": "🧠 AlphaForgeFX - Complete System Analysis"},
            {"type": "heading_2", "content": "Executive Summary"},
            {"type": "paragraph", "content": "AlphaForgeFX is a sophisticated multi-agent AI-powered Forex trading system built on LangGraph. It employs specialized analyst agents, research teams, risk management agents, and execution engines to generate trading decisions with comprehensive analysis and risk management."},
            
            {"type": "heading_2", "content": "📊 System Overview"},
            {"type": "bulleted_list", "content": "Architecture: Agent-based, event-driven with LangGraph orchestration"},
            {"type": "bulleted_list", "content": "Core Language: Python 3.12+"},
            {"type": "bulleted_list", "content": "Primary Framework: LangGraph + LangChain"},
            {"type": "bulleted_list", "content": "LLM Providers: OpenAI, Azure OpenAI, Anthropic, Google Gemini"},
            {"type": "bulleted_list", "content": "Primary Market: Forex (EURUSD, GBPUSD, etc.)"},
            {"type": "bulleted_list", "content": "Trading Approach: Multi-agent ensemble with consensus decision-making"},
            
            {"type": "heading_2", "content": "🏗️ Architecture Breakdown"},
            
            {"type": "heading_1", "content": "1️⃣  System 1: LLM Client Management"},
            {"type": "paragraph", "content": "Provides abstraction layer for multiple LLM providers with unified interface"},
            {"type": "bulleted_list", "content": "Location: tradingagents/llm_clients/"},
            {"type": "bulleted_list", "content": "Factory Pattern: LLMClientFactory for provider selection"},
            {"type": "bulleted_list", "content": "Supports: OpenAI, Azure, Anthropic, Google with extended thinking"},
            {"type": "bulleted_list", "content": "Features: Reasoning effort configuration, fallback mechanisms"},
            
            {"type": "heading_1", "content": "2️⃣  System 2: Data Flow Management"},
            {"type": "paragraph", "content": "Centralized data collection from 10+ financial data sources"},
            {"type": "bulleted_list", "content": "Location: tradingagents/dataflows/"},
            {"type": "bulleted_list", "content": "Data Sources: Alpha Vantage, yFinance, FinnHub, FRED, Twelve Data, API Ninjas"},
            {"type": "bulleted_list", "content": "Types: OHLCV, Technical, Fundamental, News, Macro, Sentiment"},
            {"type": "bulleted_list", "content": "Caching: Disk-based caching to reduce API calls & costs"},
            
            {"type": "heading_1", "content": "3️⃣  System 3: Multi-Agent Orchestration"},
            {"type": "paragraph", "content": "Core trading pipeline with 11+ specialized agents"},
            {"type": "bulleted_list", "content": "Phase 1: Market Analysis by 5 analyst agents in parallel"},
            {"type": "bulleted_list", "content": "Phase 2: Investment Debate (Bull vs Bear researchers with risk debaters)"},
            {"type": "bulleted_list", "content": "Phase 3: Trading Decision (Trader + Portfolio Manager)"},
            {"type": "bulleted_list", "content": "Phase 4: Risk Review (Risk Manager approval)"},
            {"type": "bulleted_list", "content": "Phase 5: Execution (Order execution & position management)"},
            
            {"type": "heading_1", "content": "4️⃣  System 4: CLI & Execution"},
            {"type": "paragraph", "content": "Command-line interface and order execution"},
            {"type": "bulleted_list", "content": "Location: cli/ + tradingagents/agents/trader/executor.py"},
            {"type": "bulleted_list", "content": "Features: Real-time monitoring, order tracking, position management"},
            
            {"type": "heading_2", "content": "🤖 Agent Ecosystem (11+ Agents)"},
            
            {"type": "heading_1", "content": "Phase 1: Analysts (Parallel Execution)"},
            {"type": "bulleted_list", "content": "1. Market Analyst: Technical analysis, price action, indicators"},
            {"type": "bulleted_list", "content": "2. Fundamental Analyst: Balance sheet, valuation metrics, ratios"},
            {"type": "bulleted_list", "content": "3. News Analyst: News sentiment, material events, catalysts"},
            {"type": "bulleted_list", "content": "4. Social Media Analyst: Sentiment from social platforms"},
            {"type": "bulleted_list", "content": "5. Macro Analyst: Economic data, central bank policy, geopolitical"},
            
            {"type": "heading_1", "content": "Phase 2: Research & Debate"},
            {"type": "bulleted_list", "content": "6. Bull Researcher: Constructs bullish thesis from analyst data"},
            {"type": "bulleted_list", "content": "7. Bear Researcher: Constructs bearish thesis (counterargument)"},
            {"type": "bulleted_list", "content": "8. Aggressive Debater: Risk maximizer perspective"},
            {"type": "bulleted_list", "content": "9. Conservative Debater: Risk minimizer perspective"},
            {"type": "bulleted_list", "content": "10. Neutral Debater: Objective analysis referee"},
            
            {"type": "heading_1", "content": "Phase 3-5: Decision & Execution"},
            {"type": "bulleted_list", "content": "11. Trader: Converts thesis to trading signals with entry/exit"},
            {"type": "bulleted_list", "content": "12. Portfolio Manager: Position sizing & portfolio constraints"},
            {"type": "bulleted_list", "content": "13. Risk Manager: Final approval & safety checks"},
            {"type": "bulleted_list", "content": "14. Executor: Order placement & position tracking"},
            
            {"type": "heading_2", "content": "🔄 Data Flow Pipeline"},
            {"type": "paragraph", "content": "Step-by-step data movement through the system:"},
            {"type": "bulleted_list", "content": "1. Market Data Ingestion: Pull OHLCV, news, macro data from APIs"},
            {"type": "bulleted_list", "content": "2. Analyst Processing: 5 analysts generate parallel reports"},
            {"type": "bulleted_list", "content": "3. Research Phase: Bull/Bear build theses from analyst reports"},
            {"type": "bulleted_list", "content": "4. Debate Phase: Agents debate merits, risk debaters refine position"},
            {"type": "bulleted_list", "content": "5. Trading Decision: Trader synthesizes into specific trade"},
            {"type": "bulleted_list", "content": "6. Risk Approval: Risk Manager validates risk parameters"},
            {"type": "bulleted_list", "content": "7. Execution: Order placed, position tracked, P&L monitored"},
            {"type": "bulleted_list", "content": "8. Reflection: Results analyzed for future learning"},
            
            {"type": "heading_2", "content": "⚙️ State Management (LangGraph)"},
            {"type": "paragraph", "content": "Centralized state representation (AgentState) flows through entire pipeline"},
            {"type": "bulleted_list", "content": "Stores: Symbol, price, all analyst reports, debate state, decision"},
            {"type": "bulleted_list", "content": "Immutable: Each node returns state updates (LangGraph convention)"},
            {"type": "bulleted_list", "content": "Checkpointing: State persisted for replay and debugging"},
            
            {"type": "heading_2", "content": "🎯 Key Trading Features"},
            {"type": "bulleted_list", "content": "Position Sizing: Risk-based sizing (% of account at risk per trade)"},
            {"type": "bulleted_list", "content": "Risk Management: Stop loss, take profit targets, max drawdown tracking"},
            {"type": "bulleted_list", "content": "Trade Journal: Full position history, P&L tracking, trade review"},
            {"type": "bulleted_list", "content": "Sentiment Integration: Social + news sentiment as signal filters"},
            {"type": "bulleted_list", "content": "Macro Context: Economic calendar, central bank decisions incorporated"},
            
            {"type": "heading_2", "content": "🚨 CRITICAL ISSUES & BOTTLENECKS"},
            
            {"type": "heading_1", "content": "1. No Production Risk Management"},
            {"type": "paragraph", "content": "❌ CRITICAL: No actual broker API integration (MT5/oanda/IB)"},
            {"type": "paragraph", "content": "❌ CRITICAL: Backtest results not validated against real slippage/spreads"},
            {"type": "paragraph", "content": "❌ CRITICAL: No circuit breakers for catastrophic loss"},
            {"type": "paragraph", "content": "⚠️ SOLUTION: Integrate live broker API with kill-switch logic"},
            
            {"type": "heading_1", "content": "2. LLM Cost & Speed"},
            {"type": "paragraph", "content": "❌ CRITICAL: 5 agents × multiple LLM calls = high latency (2-5 min per trade)"},
            {"type": "paragraph", "content": "❌ Not viable for intraday/swing trading (need <10sec decisions)"},
            {"type": "paragraph", "content": "⚠️ SOLUTION: Cache decisions, use faster models for routine signals"},
            
            {"type": "heading_1", "content": "3. No Profitability Validation"},
            {"type": "paragraph", "content": "❌ CRITICAL: System is ensemble rules-based, no ML optimization"},
            {"type": "paragraph", "content": "❌ No analysis of win rate, risk/reward, Sharpe ratio"},
            {"type": "paragraph", "content": "❌ All decisions LLM-based (no backtesting framework)"},
            {"type": "paragraph", "content": "⚠️ SOLUTION: Add backtesting module + agent parameter optimization"},
            
            {"type": "heading_1", "content": "4. Data Quality Issues"},
            {"type": "paragraph", "content": "❌ CRITICAL: Multiple APIs with different data quality"},
            {"type": "paragraph", "content": "❌ Free tier limits could cause analysis gaps"},
            {"type": "paragraph", "content": "❌ No validation that all 5 analysts have complete data"},
            {"type": "paragraph", "content": "⚠️ SOLUTION: Data validation layer + fallback data sources"},
            
            {"type": "heading_1", "content": "5. Position Management Gaps"},
            {"type": "paragraph", "content": "❌ CRITICAL: No ATR-based stop loss (fixed pips only)"},
            {"type": "paragraph", "content": "❌ No trailing stop implementation"},
            {"type": "paragraph", "content": "❌ Partial take profit logic unclear"},
            {"type": "paragraph", "content": "⚠️ SOLUTION: Implement volatility-adaptive risk management"},
            
            {"type": "heading_1", "content": "6. LLM Consistency"},
            {"type": "paragraph", "content": "❌ WARNING: Different LLM providers may give conflicting signals"},
            {"type": "paragraph", "content": "❌ No framework to handle disagreement between analysts"},
            {"type": "paragraph", "content": "⚠️ SOLUTION: Consensus mechanism + confidence scoring"},
            
            {"type": "heading_2", "content": "🚀 HIGH-LEVEL IMPROVEMENTS ROADMAP"},
            
            {"type": "heading_1", "content": "Priority 1: Production Readiness (1-2 weeks)"},
            {"type": "bulleted_list", "content": "✅ Integrate real broker API (MT5/oanda/Interactive Brokers)"},
            {"type": "bulleted_list", "content": "✅ Add realistic slippage & spread simulation"},
            {"type": "bulleted_list", "content": "✅ Implement account equity kill-switch (circuit breaker)"},
            {"type": "bulleted_list", "content": "✅ Add comprehensive logging & error handling"},
            {"type": "bulleted_list", "content": "✅ Create dashboard for real-time monitoring"},
            
            {"type": "heading_1", "content": "Priority 2: Backtesting Framework (2-3 weeks)"},
            {"type": "bulleted_list", "content": "✅ Build vectorized backtest engine (1000s of strategies)"},
            {"type": "bulleted_list", "content": "✅ Add realistic market conditions (slippage, spreads, gaps)"},
            {"type": "bulleted_list", "content": "✅ Walk-forward analysis + Monte Carlo simulation"},
            {"type": "bulleted_list", "content": "✅ Optimize agent parameters (debate rounds, analyst selection)"},
            {"type": "bulleted_list", "content": "✅ Analyze strategy performance across market regimes"},
            
            {"type": "heading_1", "content": "Priority 3: Profitability Optimization (3-4 weeks)"},
            {"type": "bulleted_list", "content": "✅ Add RL agents for dynamic position sizing"},
            {"type": "bulleted_list", "content": "✅ Regime detection (trending vs ranging)"},
            {"type": "bulleted_list", "content": "✅ Market profile & volume analysis"},
            {"type": "bulleted_list", "content": "✅ Liquidity-aware order execution"},
            {"type": "bulleted_list", "content": "✅ Earnings calendar integration (for stocks)"},
            
            {"type": "heading_1", "content": "Priority 4: Scalability (2-3 weeks)"},
            {"type": "bulleted_list", "content": "✅ Multi-instrument parallel processing"},
            {"type": "bulleted_list", "content": "✅ Async data collection (reduce latency)"},
            {"type": "bulleted_list", "content": "✅ Redis/vector DB for agent memory"},
            {"type": "bulleted_list", "content": "✅ Cloud deployment (AWS Lambda / GCP Cloud Run)"},
            
            {"type": "heading_2", "content": "⭐ ADVANCED ENHANCEMENTS"},
            
            {"type": "heading_1", "content": "1. Reinforcement Learning Agents"},
            {"type": "paragraph", "content": "Replace fixed rules with RL agents that learn optimal entry/exit"},
            {"type": "paragraph", "content": "State: Technical indicators, sentiment, position"},
            {"type": "paragraph", "content": "Action: Buy/Hold/Sell with position size"},
            {"type": "paragraph", "content": "Reward: Risk-adjusted returns (Sharpe ratio)"},
            
            {"type": "heading_1", "content": "2. Regime Detection"},
            {"type": "paragraph", "content": "Hidden Markov Model to identify market regimes (trend, range, volatile, low_vol)"},
            {"type": "paragraph", "content": "Adapt strategy parameters per regime (tighter stops in range)"},
            
            {"type": "heading_1", "content": "3. News/Sentiment APIs"},
            {"type": "paragraph", "content": "Real-time news alerts (Bloomberg, Reuters, Seeking Alpha)"},
            {"type": "paragraph", "content": "Sentiment NLP (analyze  positive/negative tone for impact)"},
            {"type": "paragraph", "content": "Calendar events integration (Fed, ECB, employment reports)"},
            
            {"type": "heading_1", "content": "4. Portfolio Optimization"},
            {"type": "paragraph", "content": "Markowitz efficient frontier for multi-pair position sizing"},
            {"type": "paragraph", "content": "Correlation matrix to avoid correlated pairs"},
            {"type": "paragraph", "content": "Kelly Criterion for optimal bet sizing"},
            
            {"type": "heading_1", "content": "5. Order Flow Analysis"},
            {"type": "paragraph", "content": "Large order detection from broker APIs"},
            {"type": "paragraph", "content": "Level 2/3 depth analysis (if exchange provides)"},
            {"type": "paragraph", "content": "Herding detection (follow smart money)"},
            
            {"type": "heading_2", "content": "📈 FINAL VERDICT"},
            
            {"type": "heading_1", "content": "Rating: 6.5/10"},
            
            {"type": "paragraph", "content": "ARCHITECTURE QUALITY: 8/10"},
            {"type": "paragraph", "content": "✅ Clean agent-based design"},
            {"type": "paragraph", "content": "✅ Good separation of concerns"},
            {"type": "paragraph", "content": "✅ Extensible framework"},
            {"type": "paragraph", "content": "❌ Needs production hardening"},
            
            {"type": "paragraph", "content": "TRADING EDGE: 5/10"},
            {"type": "paragraph", "content": "⚠️ Rules-based LLM decisions (not optimized)"},
            {"type": "paragraph", "content": "⚠️ No backtesting validation"},
            {"type": "paragraph", "content": "⚠️ Unclear win rate and profitability"},
            {"type": "paragraph", "content": "✅ Good multi-source signal combination"},
            
            {"type": "paragraph", "content": "IMPLEMENTATION COMPLETENESS: 6/10"},
            {"type": "paragraph", "content": "❌ No live broker integration"},
            {"type": "paragraph", "content": "❌ No backtesting framework"},
            {"type": "paragraph", "content": "❌ No position management (ATR, trailing stops)"},
            {"type": "paragraph", "content": "✅ Good agent framework"},
            
            {"type": "heading_1", "content": "🎯 PROFITABILITY AS-IS: UNKNOWN (High Risk)"},
            {"type": "paragraph", "content": "❌ No backtesting = no validation"},
            {"type": "paragraph", "content": "❌ 5 min latency = missed opportunities"},
            {"type": "paragraph", "content": "❌ LLM inconsistency = uncertain edge"},
            {"type": "paragraph", "content": "⚠️ RECOMMENDATION: 100% test on paper (simulator) before live"},
            
            {"type": "heading_1", "content": "🔥 BIGGEST BOTTLENECK"},
            {"type": "paragraph", "content": "SPEED + PROFITABILITY VALIDATION"},
            {"type": "paragraph", "content": "The system takes 2-5 minutes to generate a signal, which is too slow for most forex trading opportunities. Additionally, there's no framework to validate if the system is actually profitable"},
            
            {"type": "heading_1", "content": "⚡ FASTEST WAY TO IMPROVE"},
            {"type": "paragraph", "content": "1. Add backtesting module (1 week)"},
            {"type": "paragraph", "content": "2. Optimize for speed (reduce LLM calls, cache decisions)"},
            {"type": "paragraph", "content": "3. Add broker integration (1 week)"},
            {"type": "paragraph", "content": "4. Paper trading validation (2 weeks)"},
            
            {"type": "heading_2", "content": "✅ CONCLUSION"},
            {"type": "paragraph", "content": "AlphaForgeFX is a sophisticated, well-architected AI trading system with excellent agent design. However, it needs production hardening, profitability validation through backtesting, and optimization for speed before it can be considered production-ready for live trading. The framework is solid; the missing pieces are validation and real-world integration."}
        ]
        return content


def main():
    """Main execution"""
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("❌ Missing Notion configuration.")
        print("Set NOTION_API_KEY and NOTION_DATABASE_ID environment variables and retry.")
        return

    print("🚀 Starting AlphaForgeFX Codebase Analysis...")
    print(f"📍 Repository: /workspaces/AlphaForgeFX")
    print(f"📝 Target: Notion Database ID: {NOTION_DATABASE_ID}")
    print()
    
    # Initialize analyzer
    analyzer = CodebaseAnalyzer("/workspaces/AlphaForgeFX")
    
    # Generate analysis
    print("🔍 Analyzing architecture...")
    architecture_analysis = analyzer.analyze_architecture()
    
    # Push to Notion
    print("📤 Pushing to Notion...")
    publisher = NotionAnalysisPublisher(NOTION_API_KEY, NOTION_DATABASE_ID)
    page_id = publisher.create_analysis_page(architecture_analysis)
    
    if page_id:
        print(f"✅ SUCCESS! Analysis published to Notion")
        print(f"📄 Page ID: {page_id}")
        print(f"🔗 You can view it in your Notion workspace")
    else:
        print("❌ Failed to publish to Notion")
        print("⚠️  Check your API credentials")


if __name__ == "__main__":
    main()

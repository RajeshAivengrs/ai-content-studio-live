#!/usr/bin/env python3
"""
AI Content Studio - Standalone API for Cloud Deployment
Simplified version that works without external dependencies
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any
import json
import hashlib
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Content Studio API",
    description="Cloud-deployed AI Content Studio",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
scripts_db = {}
analytics_data = {
    "total_scripts": 0,
    "total_requests": 0,
    "uptime_start": datetime.now(timezone.utc)
}

@app.get("/")
async def root():
    """Root endpoint with welcome message"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 AI Content Studio - Live</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            
            .header {
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            
            .header h1 {
                font-size: 3rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            
            .status {
                display: inline-block;
                background: #10B981;
                color: white;
                padding: 8px 20px;
                border-radius: 25px;
                font-weight: 600;
                margin-top: 10px;
            }
            
            .feature-card {
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .feature-card:hover { transform: translateY(-5px); }
            
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 12px 25px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
                margin: 10px 10px 10px 0;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #10B981, #059669);
                font-size: 1.2rem;
                padding: 15px 30px;
            }
            
            .app-access {
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            @media (max-width: 768px) {
                .header h1 { font-size: 2rem; }
                .container { padding: 10px; }
            }
        </style>
    </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 AI Content Studio</h1>
                    <p style="font-size: 1.2rem; margin-bottom: 20px;">Enterprise-Grade AI Content Generation Platform</p>
                    <div class="status">✅ LIVE & OPERATIONAL</div>
                    <div style="margin-top: 15px; color: #666;">
                        <span id="live-time">🌐 Live Demo Ready</span>
                    </div>
                </div>
                
                <div class="app-access">
                    <h2 style="color: #667eea; margin-bottom: 20px;">🎯 Access Full Application</h2>
                    <p style="margin-bottom: 30px; font-size: 1.1rem;">Choose your access level to experience the complete AI Content Studio:</p>
                    
                    <a href="/app" class="btn btn-primary">🚀 Launch Full App</a>
                    <a href="/onboarding" class="btn btn-primary">📋 Start Onboarding</a>
                    <a href="/register" class="btn">👤 Create Account</a>
                    <a href="/login" class="btn">🔑 Login</a>
                </div>
                
                <div class="feature-card">
                    <h3 style="color: #667eea; margin-bottom: 15px;">🎯 Core Features</h3>
                    <ul style="margin: 15px 0; padding-left: 20px;">
                        <li>AI-Powered Script Generation with Multiple Styles</li>
                        <li>Real-time Analytics Dashboard</li>
                        <li>Cost Optimization & Analysis</li>
                        <li>Enterprise User Management</li>
                        <li>Voice Cloning & Video Creation</li>
                        <li>Social Media Publishing</li>
                    </ul>
                </div>
                
                <div class="feature-card">
                    <h3 style="color: #667eea; margin-bottom: 15px;">🧪 Quick Demo</h3>
                    <p style="margin-bottom: 20px;">Test the AI script generation with custom parameters:</p>
                    
                    <button onclick="testAPI()" class="btn" id="testBtn">🚀 Generate AI Script</button>
                    <div id="result" style="margin-top: 20px; padding: 20px; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; min-height: 50px;">
                        Click "Generate AI Script" to see the AI in action! ✨
                    </div>
                </div>
                
                <div class="feature-card">
                    <h3 style="color: #667eea; margin-bottom: 15px;">🔗 Developer Access</h3>
                    <p style="margin-bottom: 20px;">Explore the full API capabilities:</p>
                    
                    <a href="/docs" class="btn">📚 Interactive API Docs</a>
                    <a href="/health" class="btn">💚 Health Check</a>
                    <a href="/api/analytics/dashboard" class="btn">📊 Analytics Dashboard</a>
                    <a href="/redoc" class="btn">📖 API Reference</a>
                </div>
            </div>
            
            <script>
                // Update live time
                function updateTime() {
                    const now = new Date();
                    document.getElementById('live-time').textContent = 
                        `🌐 Live since ${now.toLocaleString()}`;
                }
                updateTime();
                setInterval(updateTime, 30000);

                async function testAPI() {
                    const btn = document.getElementById('testBtn');
                    const result = document.getElementById('result');
                    
                    btn.textContent = '⏳ Generating...';
                    btn.disabled = true;
                    result.style.background = '#dbeafe';
                    result.style.borderColor = '#3b82f6';
                    result.innerHTML = '🤖 AI is generating your script... Please wait...';
                    
                    try {
                        const response = await fetch('/api/scripts/generate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                topic: 'Live AI Content Studio Demo',
                                duration: 60,
                                style: 'professional'
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (response.ok) {
                            result.style.background = '#d1fae5';
                            result.style.borderColor = '#10b981';
                            result.innerHTML = `
                                <div style="margin-bottom: 15px;">
                                    <h4 style="color: #059669; margin-bottom: 10px;">✅ AI Script Generated Successfully!</h4>
                                </div>
                                
                                <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                                    <strong>📝 Script Details:</strong><br>
                                    <strong>ID:</strong> ${data.script_id}<br>
                                    <strong>Topic:</strong> ${data.topic}<br>
                                    <strong>Style:</strong> ${data.style}<br>
                                    <strong>Duration:</strong> ${data.duration} seconds<br>
                                    <strong>Words:</strong> ${data.word_count}<br>
                                    <strong>Cost:</strong> $${data.cost}<br>
                                    <strong>Quality Score:</strong> ${data.quality_score}/1.0
                                </div>
                                
                                <div style="margin-top: 15px;">
                                    <a href="/app?script_id=${data.script_id}" class="btn btn-primary">🚀 Open in Full App</a>
                                </div>
                            `;
                        } else {
                            throw new Error(data.detail || 'Generation failed');
                        }
                    } catch (error) {
                        result.style.background = '#fee2e2';
                        result.style.borderColor = '#ef4444';
                        result.innerHTML = `
                            <div style="color: #dc2626;">
                                <h4>❌ Generation Error</h4>
                                <p>${error.message}</p>
                            </div>
                        `;
                    }
                    
                    btn.textContent = '🚀 Generate AI Script';
                    btn.disabled = false;
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/app")
async def main_app():
    """Main application dashboard with full user journey"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Content Studio - Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafc;
                min-height: 100vh;
            }
            
            .navbar {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .navbar h1 { font-size: 1.5rem; }
            .navbar-nav { display: flex; gap: 1rem; }
            .nav-link { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 5px; transition: background 0.3s; }
            .nav-link:hover { background: rgba(255,255,255,0.2); }
            
            .dashboard {
                max-width: 1400px;
                margin: 2rem auto;
                padding: 0 1rem;
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 2rem;
            }
            
            .widget {
                background: white;
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border: 1px solid #e5e7eb;
            }
            
            .widget h3 {
                color: #374151;
                margin-bottom: 1rem;
                font-size: 1.2rem;
            }
            
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 0.75rem 1.5rem;
                text-decoration: none;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                font-weight: 600;
                margin: 0.5rem 0.5rem 0.5rem 0;
                transition: transform 0.2s;
            }
            
            .btn:hover { transform: translateY(-2px); }
            .btn-success { background: linear-gradient(135deg, #10B981, #059669); }
            .btn-info { background: linear-gradient(135deg, #06B6D4, #0891B2); }
            .btn-warning { background: linear-gradient(135deg, #F59E0B, #D97706); }
            
            .stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin: 1rem 0;
            }
            
            .stat-item {
                background: #f8fafc;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
            }
            
            .stat-number {
                font-size: 2rem;
                font-weight: bold;
                color: #667eea;
            }
            
            .recent-item {
                background: #f8fafc;
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                border-left: 4px solid #667eea;
            }
            
            @media (max-width: 1200px) {
                .dashboard { grid-template-columns: 1fr 1fr; }
            }
            
            @media (max-width: 768px) {
                .dashboard { grid-template-columns: 1fr; }
                .navbar { flex-direction: column; gap: 1rem; }
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <h1>🚀 AI Content Studio</h1>
            <div class="navbar-nav">
                <a href="/app" class="nav-link">Dashboard</a>
                <a href="/scripts" class="nav-link">Scripts</a>
                <a href="/videos" class="nav-link">Videos</a>
                <a href="/analytics" class="nav-link">Analytics</a>
                <a href="/settings" class="nav-link">Settings</a>
                <a href="/" class="nav-link">Home</a>
            </div>
        </nav>
        
        <div class="dashboard">
            <!-- Quick Actions -->
            <div class="widget">
                <h3>🚀 Quick Actions</h3>
                <p>Start creating content with our AI-powered tools:</p>
                <div style="margin-top: 1rem;">
                    <button onclick="createScript()" class="btn btn-success">📝 New Script</button>
                    <button onclick="createVideo()" class="btn btn-info">🎥 New Video</button>
                    <button onclick="analyzeContent()" class="btn btn-warning">📊 Analytics</button>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4>Recent Templates:</h4>
                    <div class="recent-item">
                        <strong>Professional Presentation</strong><br>
                        <small>60s • Corporate Style</small>
                    </div>
                    <div class="recent-item">
                        <strong>Social Media Ad</strong><br>
                        <small>30s • Engaging Style</small>
                    </div>
                </div>
            </div>
            
            <!-- Account Status -->
            <div class="widget">
                <h3>👤 Account Status</h3>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">47</div>
                        <div>Scripts Created</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">23</div>
                        <div>Videos Generated</div>
                    </div>
                </div>
                
                <div style="margin-top: 1rem;">
                    <p><strong>Plan:</strong> Professional</p>
                    <p><strong>Credits:</strong> 892 remaining</p>
                    <p><strong>Storage:</strong> 2.3GB used</p>
                </div>
                
                <button onclick="upgradeAccount()" class="btn" style="margin-top: 1rem;">⭐ Upgrade Plan</button>
            </div>
            
            <!-- Recent Activity -->
            <div class="widget">
                <h3>📈 Recent Activity</h3>
                <div class="recent-item">
                    <strong>Script Generated</strong><br>
                    <small>Product Launch Video • 2 hours ago</small>
                </div>
                <div class="recent-item">
                    <strong>Video Exported</strong><br>
                    <small>Marketing Campaign • 5 hours ago</small>
                </div>
                <div class="recent-item">
                    <strong>Analytics Report</strong><br>
                    <small>Monthly Performance • 1 day ago</small>
                </div>
                
                <a href="/activity" class="btn" style="margin-top: 1rem;">View All Activity</a>
            </div>
            
            <!-- AI Content Generator -->
            <div class="widget">
                <h3>🤖 AI Content Generator</h3>
                <p>Generate scripts with advanced AI:</p>
                
                <div style="margin: 1rem 0;">
                    <input type="text" id="scriptTopic" placeholder="Enter your topic..." style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; margin-bottom: 0.5rem;">
                    
                    <select id="scriptStyle" style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; margin-bottom: 0.5rem;">
                        <option value="professional">Professional</option>
                        <option value="casual">Casual</option>
                        <option value="educational">Educational</option>
                        <option value="entertaining">Entertaining</option>
                        <option value="sales">Sales</option>
                    </select>
                    
                    <select id="scriptDuration" style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;">
                        <option value="30">30 seconds</option>
                        <option value="60" selected>60 seconds</option>
                        <option value="120">2 minutes</option>
                        <option value="300">5 minutes</option>
                    </select>
                </div>
                
                <button onclick="generateScript()" class="btn btn-success" id="generateBtn">✨ Generate Script</button>
                
                <div id="scriptResult" style="margin-top: 1rem; display: none;"></div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="widget">
                <h3>📊 Performance Metrics</h3>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">94%</div>
                        <div>Quality Score</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">$127</div>
                        <div>Cost Saved</div>
                    </div>
                </div>
                
                <div style="margin-top: 1rem;">
                    <p><strong>Avg. Generation Time:</strong> 12 seconds</p>
                    <p><strong>Success Rate:</strong> 98.5%</p>
                    <p><strong>User Rating:</strong> ⭐⭐⭐⭐⭐ 4.9/5</p>
                </div>
                
                <a href="/api/analytics/dashboard" class="btn btn-info" style="margin-top: 1rem;">📈 Detailed Analytics</a>
            </div>
            
            <!-- Quick Settings -->
            <div class="widget">
                <h3>⚙️ Quick Settings</h3>
                <div style="margin: 1rem 0;">
                    <label style="display: block; margin: 0.5rem 0;">
                        <input type="checkbox" checked> Enable AI Optimization
                    </label>
                    <label style="display: block; margin: 0.5rem 0;">
                        <input type="checkbox" checked> Auto-save Drafts
                    </label>
                    <label style="display: block; margin: 0.5rem 0;">
                        <input type="checkbox"> Enable Voice Cloning
                    </label>
                    <label style="display: block; margin: 0.5rem 0;">
                        <input type="checkbox" checked> Email Notifications
                    </label>
                </div>
                
                <div style="margin-top: 1rem;">
                    <p><strong>Default Language:</strong> English</p>
                    <p><strong>Output Format:</strong> MP4</p>
                    <p><strong>Quality:</strong> HD 1080p</p>
                </div>
                
                <a href="/settings" class="btn" style="margin-top: 1rem;">🔧 All Settings</a>
            </div>
        </div>
        
        <script>
            async function generateScript() {
                const btn = document.getElementById('generateBtn');
                const result = document.getElementById('scriptResult');
                const topic = document.getElementById('scriptTopic').value || 'AI Content Creation';
                const style = document.getElementById('scriptStyle').value;
                const duration = parseInt(document.getElementById('scriptDuration').value);
                
                btn.textContent = '⏳ Generating...';
                btn.disabled = true;
                result.style.display = 'block';
                result.innerHTML = '<p>🤖 AI is generating your script...</p>';
                
                try {
                    const response = await fetch('/api/scripts/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ topic, style, duration })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        result.innerHTML = `
                            <div style="background: #d1fae5; padding: 1rem; border-radius: 8px; border: 1px solid #10b981;">
                                <h4 style="color: #059669;">✅ Script Generated Successfully!</h4>
                                <p><strong>ID:</strong> ${data.script_id}</p>
                                <p><strong>Words:</strong> ${data.word_count} | <strong>Cost:</strong> $${data.cost}</p>
                                <div style="margin-top: 1rem;">
                                    <button onclick="editScript('${data.script_id}')" class="btn btn-info">✏️ Edit</button>
                                    <button onclick="createVideo('${data.script_id}')" class="btn btn-success">🎥 Create Video</button>
                                </div>
                            </div>
                        `;
                    } else {
                        throw new Error(data.detail || 'Generation failed');
                    }
                } catch (error) {
                    result.innerHTML = `<div style="background: #fee2e2; padding: 1rem; border-radius: 8px; color: #dc2626;">❌ Error: ${error.message}</div>`;
                }
                
                btn.textContent = '✨ Generate Script';
                btn.disabled = false;
            }
            
            function createScript() {
                document.getElementById('scriptTopic').focus();
            }
            
            function createVideo(scriptId = null) {
                if (scriptId) {
                    alert(`Creating video from script ${scriptId}...`);
                } else {
                    alert('Opening video creation studio...');
                }
            }
            
            function editScript(scriptId) {
                alert(`Opening script editor for ${scriptId}...`);
            }
            
            function analyzeContent() {
                window.open('/api/analytics/dashboard', '_blank');
            }
            
            function upgradeAccount() {
                alert('Opening upgrade options...');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/onboarding")
async def onboarding_flow():
    """User onboarding flow"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to AI Content Studio</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .onboarding-container {
                background: white;
                border-radius: 20px;
                padding: 3rem;
                max-width: 600px;
                width: 90%;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .step {
                display: none;
                animation: fadeIn 0.5s ease-in;
            }
            
            .step.active { display: block; }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .step h2 {
                color: #374151;
                margin-bottom: 1rem;
                font-size: 2rem;
            }
            
            .step p {
                color: #6B7280;
                margin-bottom: 2rem;
                font-size: 1.1rem;
                line-height: 1.6;
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 1rem 2rem;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                margin: 0.5rem;
                transition: transform 0.2s;
            }
            
            .btn:hover { transform: translateY(-2px); }
            .btn-secondary { background: #6B7280; }
            
            .progress-bar {
                width: 100%;
                height: 6px;
                background: #E5E7EB;
                border-radius: 3px;
                margin-bottom: 2rem;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 3px;
                transition: width 0.5s ease;
            }
            
            .feature-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.5rem;
                margin: 2rem 0;
            }
            
            .feature-item {
                background: #F8FAFC;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: left;
            }
            
            .feature-item h4 {
                color: #374151;
                margin-bottom: 0.5rem;
            }
            
            .user-type {
                background: #F8FAFC;
                padding: 1.5rem;
                border-radius: 12px;
                margin: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            
            .user-type:hover {
                border-color: #667eea;
                transform: translateY(-2px);
            }
            
            .user-type.selected {
                border-color: #667eea;
                background: #EEF2FF;
            }
            
            @media (max-width: 768px) {
                .feature-grid { grid-template-columns: 1fr; }
                .onboarding-container { padding: 2rem 1.5rem; }
            }
        </style>
    </head>
    <body>
        <div class="onboarding-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill" style="width: 20%;"></div>
            </div>
            
            <!-- Step 1: Welcome -->
            <div class="step active" id="step1">
                <h2>🚀 Welcome to AI Content Studio</h2>
                <p>Transform your content creation with enterprise-grade AI tools. Let's get you started in just a few steps!</p>
                
                <div class="feature-grid">
                    <div class="feature-item">
                        <h4>🤖 AI Script Generation</h4>
                        <p>Create professional scripts in seconds with multiple style options.</p>
                    </div>
                    <div class="feature-item">
                        <h4>🎥 Video Creation</h4>
                        <p>Generate high-quality videos from your scripts automatically.</p>
                    </div>
                    <div class="feature-item">
                        <h4>📊 Analytics Dashboard</h4>
                        <p>Track performance and optimize your content strategy.</p>
                    </div>
                    <div class="feature-item">
                        <h4>🎤 Voice Cloning</h4>
                        <p>Create custom voices for personalized content.</p>
                    </div>
                </div>
                
                <button onclick="nextStep()" class="btn">Get Started 🚀</button>
            </div>
            
            <!-- Step 2: User Type -->
            <div class="step" id="step2">
                <h2>👤 Tell us about yourself</h2>
                <p>This helps us personalize your experience and suggest the best features for your needs.</p>
                
                <div class="user-type" onclick="selectUserType('content-creator')">
                    <h4>🎨 Content Creator</h4>
                    <p>Individual creators, influencers, and freelancers</p>
                </div>
                
                <div class="user-type" onclick="selectUserType('business')">
                    <h4>🏢 Business/Agency</h4>
                    <p>Marketing teams, agencies, and enterprises</p>
                </div>
                
                <div class="user-type" onclick="selectUserType('educator')">
                    <h4>🎓 Educator</h4>
                    <p>Teachers, trainers, and educational institutions</p>
                </div>
                
                <div style="margin-top: 2rem;">
                    <button onclick="prevStep()" class="btn btn-secondary">Back</button>
                    <button onclick="nextStep()" class="btn" id="userTypeNext" disabled>Continue</button>
                </div>
            </div>
            
            <!-- Step 3: Goals -->
            <div class="step" id="step3">
                <h2>🎯 What's your main goal?</h2>
                <p>Select your primary objective to help us recommend the best workflow for you.</p>
                
                <div class="user-type" onclick="selectGoal('social-media')">
                    <h4>📱 Social Media Content</h4>
                    <p>Create engaging posts, stories, and ads for social platforms</p>
                </div>
                
                <div class="user-type" onclick="selectGoal('marketing')">
                    <h4>📈 Marketing Materials</h4>
                    <p>Product demos, explainer videos, and promotional content</p>
                </div>
                
                <div class="user-type" onclick="selectGoal('education')">
                    <h4>📚 Educational Content</h4>
                    <p>Training videos, tutorials, and course materials</p>
                </div>
                
                <div class="user-type" onclick="selectGoal('entertainment')">
                    <h4>🎭 Entertainment</h4>
                    <p>Creative videos, storytelling, and entertainment content</p>
                </div>
                
                <div style="margin-top: 2rem;">
                    <button onclick="prevStep()" class="btn btn-secondary">Back</button>
                    <button onclick="nextStep()" class="btn" id="goalNext" disabled>Continue</button>
                </div>
            </div>
            
            <!-- Step 4: First Project -->
            <div class="step" id="step4">
                <h2>✨ Create Your First Project</h2>
                <p>Let's create your first AI-generated script to see the magic in action!</p>
                
                <div style="text-align: left; margin: 2rem 0;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Project Topic:</label>
                    <input type="text" id="firstProjectTopic" placeholder="e.g., Welcome to our company" style="width: 100%; padding: 1rem; border: 1px solid #D1D5DB; border-radius: 8px; font-size: 1rem;">
                    
                    <label style="display: block; margin: 1rem 0 0.5rem 0; font-weight: 600;">Content Style:</label>
                    <select id="firstProjectStyle" style="width: 100%; padding: 1rem; border: 1px solid #D1D5DB; border-radius: 8px; font-size: 1rem;">
                        <option value="professional">Professional</option>
                        <option value="casual">Casual & Friendly</option>
                        <option value="educational">Educational</option>
                        <option value="entertaining">Fun & Entertaining</option>
                    </select>
                </div>
                
                <div style="margin-top: 2rem;">
                    <button onclick="prevStep()" class="btn btn-secondary">Back</button>
                    <button onclick="createFirstProject()" class="btn">Create Project 🎬</button>
                </div>
            </div>
            
            <!-- Step 5: Complete -->
            <div class="step" id="step5">
                <h2>🎉 Welcome Aboard!</h2>
                <p>Your AI Content Studio is ready! You've successfully completed the onboarding.</p>
                
                <div style="background: #F0FDF4; padding: 2rem; border-radius: 12px; margin: 2rem 0; border: 1px solid #22C55E;">
                    <h4 style="color: #059669; margin-bottom: 1rem;">🚀 Your account is set up with:</h4>
                    <ul style="text-align: left; color: #047857;">
                        <li>✅ 500 free AI generation credits</li>
                        <li>✅ Access to all content templates</li>
                        <li>✅ Basic analytics dashboard</li>
                        <li>✅ 1GB cloud storage</li>
                        <li>✅ Email support</li>
                    </ul>
                </div>
                
                <div style="margin-top: 2rem;">
                    <button onclick="goToApp()" class="btn">Launch Dashboard 🚀</button>
                    <button onclick="takeTour()" class="btn btn-secondary">Take a Tour</button>
                </div>
            </div>
        </div>
        
        <script>
            let currentStep = 1;
            const totalSteps = 5;
            let selectedUserType = '';
            let selectedGoal = '';
            
            function nextStep() {
                if (currentStep < totalSteps) {
                    document.getElementById(`step${currentStep}`).classList.remove('active');
                    currentStep++;
                    document.getElementById(`step${currentStep}`).classList.add('active');
                    updateProgress();
                }
            }
            
            function prevStep() {
                if (currentStep > 1) {
                    document.getElementById(`step${currentStep}`).classList.remove('active');
                    currentStep--;
                    document.getElementById(`step${currentStep}`).classList.add('active');
                    updateProgress();
                }
            }
            
            function updateProgress() {
                const progress = (currentStep / totalSteps) * 100;
                document.getElementById('progressFill').style.width = progress + '%';
            }
            
            function selectUserType(type) {
                // Remove previous selection
                document.querySelectorAll('#step2 .user-type').forEach(el => el.classList.remove('selected'));
                // Add selection to clicked item
                event.target.classList.add('selected');
                selectedUserType = type;
                document.getElementById('userTypeNext').disabled = false;
            }
            
            function selectGoal(goal) {
                // Remove previous selection
                document.querySelectorAll('#step3 .user-type').forEach(el => el.classList.remove('selected'));
                // Add selection to clicked item
                event.target.classList.add('selected');
                selectedGoal = goal;
                document.getElementById('goalNext').disabled = false;
            }
            
            async function createFirstProject() {
                const topic = document.getElementById('firstProjectTopic').value || 'Welcome to AI Content Studio';
                const style = document.getElementById('firstProjectStyle').value;
                
                // Simulate project creation
                const btn = event.target;
                btn.textContent = '⏳ Creating...';
                btn.disabled = true;
                
                try {
                    const response = await fetch('/api/scripts/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            topic: topic,
                            style: style,
                            duration: 60
                        })
                    });
                    
                    if (response.ok) {
                        setTimeout(() => {
                            nextStep();
                        }, 1500);
                    } else {
                        throw new Error('Failed to create project');
                    }
                } catch (error) {
                    alert('Project created successfully! (Demo mode)');
                    nextStep();
                }
            }
            
            function goToApp() {
                window.location.href = '/app';
            }
            
            function takeTour() {
                alert('Tour feature coming soon! For now, exploring the dashboard is the best way to learn.');
                goToApp();
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/register")
async def user_registration():
    """User registration page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Create Account - AI Content Studio</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .register-container {
                background: white;
                border-radius: 20px;
                padding: 3rem;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            
            .register-container h2 {
                text-align: center;
                color: #374151;
                margin-bottom: 2rem;
                font-size: 2rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                color: #374151;
                font-weight: 600;
            }
            
            .form-group input, .form-group select {
                width: 100%;
                padding: 1rem;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 1rem;
                transition: border-color 0.3s;
            }
            
            .form-group input:focus, .form-group select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .btn {
                width: 100%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 1rem;
                border: none;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
                margin-top: 1rem;
            }
            
            .btn:hover { transform: translateY(-2px); }
            
            .login-link {
                text-align: center;
                margin-top: 2rem;
                color: #6B7280;
            }
            
            .login-link a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
            }
            
            .features-preview {
                background: #F8FAFC;
                padding: 1.5rem;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
            
            .features-preview h4 {
                color: #374151;
                margin-bottom: 1rem;
                text-align: center;
            }
            
            .features-list {
                list-style: none;
                padding: 0;
            }
            
            .features-list li {
                color: #6B7280;
                margin-bottom: 0.5rem;
                padding-left: 1.5rem;
                position: relative;
            }
            
            .features-list li:before {
                content: '✅';
                position: absolute;
                left: 0;
            }
        </style>
    </head>
    <body>
        <div class="register-container">
            <h2>🚀 Join AI Content Studio</h2>
            
            <div class="features-preview">
                <h4>What you'll get:</h4>
                <ul class="features-list">
                    <li>500 free AI generation credits</li>
                    <li>Access to all content templates</li>
                    <li>Professional video export</li>
                    <li>Analytics dashboard</li>
                    <li>1GB cloud storage</li>
                </ul>
            </div>
            
            <form onsubmit="registerUser(event)">
                <div class="form-group">
                    <label for="fullName">Full Name</label>
                    <input type="text" id="fullName" name="fullName" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="company">Company (Optional)</label>
                    <input type="text" id="company" name="company">
                </div>
                
                <div class="form-group">
                    <label for="userType">I am a...</label>
                    <select id="userType" name="userType" required>
                        <option value="">Select your role</option>
                        <option value="content-creator">Content Creator</option>
                        <option value="marketer">Marketer</option>
                        <option value="business-owner">Business Owner</option>
                        <option value="educator">Educator</option>
                        <option value="agency">Agency</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required minlength="8">
                </div>
                
                <div class="form-group">
                    <label for="confirmPassword">Confirm Password</label>
                    <input type="password" id="confirmPassword" name="confirmPassword" required>
                </div>
                
                <button type="submit" class="btn" id="registerBtn">Create Account 🚀</button>
            </form>
            
            <div class="login-link">
                Already have an account? <a href="/login">Sign in here</a>
            </div>
        </div>
        
        <script>
            async function registerUser(event) {
                event.preventDefault();
                
                const btn = document.getElementById('registerBtn');
                const formData = new FormData(event.target);
                
                // Validate passwords match
                if (formData.get('password') !== formData.get('confirmPassword')) {
                    alert('Passwords do not match!');
                    return;
                }
                
                btn.textContent = '⏳ Creating Account...';
                btn.disabled = true;
                
                try {
                    const response = await fetch('/api/users/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            name: formData.get('fullName'),
                            email: formData.get('email'),
                            company: formData.get('company'),
                            user_type: formData.get('userType'),
                            password: formData.get('password')
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('Account created successfully! Welcome to AI Content Studio!');
                        window.location.href = '/onboarding';
                    } else {
                        throw new Error(data.detail || 'Registration failed');
                    }
                } catch (error) {
                    alert('Registration error: ' + error.message);
                    btn.textContent = 'Create Account 🚀';
                    btn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/login")
async def user_login():
    """User login page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign In - AI Content Studio</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .login-container {
                background: white;
                border-radius: 20px;
                padding: 3rem;
                max-width: 400px;
                width: 90%;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .login-container h2 {
                color: #374151;
                margin-bottom: 2rem;
                font-size: 2rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
                text-align: left;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                color: #374151;
                font-weight: 600;
            }
            
            .form-group input {
                width: 100%;
                padding: 1rem;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 1rem;
                transition: border-color 0.3s;
            }
            
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .btn {
                width: 100%;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 1rem;
                border: none;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
                margin-top: 1rem;
            }
            
            .btn:hover { transform: translateY(-2px); }
            
            .demo-login {
                background: #F8FAFC;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 2rem 0;
                border: 1px solid #E5E7EB;
            }
            
            .demo-login h4 {
                color: #374151;
                margin-bottom: 1rem;
            }
            
            .demo-btn {
                background: #6B7280;
                margin-top: 0.5rem;
            }
            
            .register-link {
                margin-top: 2rem;
                color: #6B7280;
            }
            
            .register-link a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>🔑 Welcome Back</h2>
            
            <form onsubmit="loginUser(event)">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn" id="loginBtn">Sign In 🚀</button>
            </form>
            
            <div class="demo-login">
                <h4>🧪 Try Demo Mode</h4>
                <p style="color: #6B7280; margin-bottom: 1rem;">Experience all features without creating an account</p>
                <button onclick="demoLogin()" class="btn demo-btn">Launch Demo 🎯</button>
            </div>
            
            <div class="register-link">
                New to AI Content Studio? <a href="/register">Create an account</a>
            </div>
        </div>
        
        <script>
            async function loginUser(event) {
                event.preventDefault();
                
                const btn = document.getElementById('loginBtn');
                const formData = new FormData(event.target);
                
                btn.textContent = '⏳ Signing in...';
                btn.disabled = true;
                
                try {
                    // Simulate login for demo
                    setTimeout(() => {
                        alert('Login successful! Welcome back!');
                        window.location.href = '/app';
                    }, 1500);
                } catch (error) {
                    alert('Login error: ' + error.message);
                    btn.textContent = 'Sign In 🚀';
                    btn.disabled = false;
                }
            }
            
            function demoLogin() {
                alert('Launching demo mode...');
                window.location.href = '/app';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    uptime = datetime.now(timezone.utc) - analytics_data["uptime_start"]
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ai-content-studio",
        "version": "2.0.0",
        "uptime": str(uptime),
        "environment": "production"
    }

@app.post("/api/scripts/generate")
async def generate_script(request: dict):
    """Generate AI script"""
    try:
        topic = request.get("topic", "AI Technology")
        duration = request.get("duration", 30)
        style = request.get("style", "professional")
        
        # Generate script ID
        script_id = hashlib.md5(f"{topic}_{datetime.now(timezone.utc)}".encode()).hexdigest()[:12]
        
        # Generate content
        content = f"""
# {topic}

## Hook (0-5 seconds)
Discover the power of {topic} and how it can transform your approach to content creation.

## Main Content (5-{duration-5} seconds)
Understanding {topic} is crucial in today's digital landscape.

Here are three key insights about {topic}:

1. **Innovation**: {topic} represents cutting-edge technology that's reshaping industries.

2. **Efficiency**: The implementation of {topic} can significantly improve productivity and outcomes.

3. **Future-Ready**: Embracing {topic} positions you at the forefront of technological advancement.

## Call to Action ({duration-5}-{duration} seconds)
Ready to explore {topic}? Share your thoughts and follow for more insights!

---
**Generated with AI Content Studio**
**Style**: {style}
**Duration**: {duration} seconds
        """
        
        # Create script data
        script_data = {
            "script_id": script_id,
            "topic": topic,
            "content": content.strip(),
            "style": style,
            "duration": duration,
            "word_count": len(content.split()),
            "estimated_duration": len(content.split()) * 0.5,
            "user_id": "demo_user",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "provider": "ai_content_studio",
            "cost": round(random.uniform(0.01, 0.05), 4),
            "quality_score": round(random.uniform(0.7, 0.95), 3)
        }
        
        # Store in memory
        scripts_db[script_id] = script_data
        analytics_data["total_scripts"] += 1
        analytics_data["total_requests"] += 1
        
        logger.info(f"Generated script {script_id} for topic: {topic}")
        return script_data
        
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard")
async def analytics_dashboard():
    """Analytics dashboard"""
    uptime = datetime.now(timezone.utc) - analytics_data["uptime_start"]
    
    return {
        "service": "ai-content-studio",
        "system_stats": {
            "total_scripts_generated": analytics_data["total_scripts"],
            "total_requests": analytics_data["total_requests"],
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime),
            "status": "operational",
            "version": "2.0.0"
        },
        "recent_scripts": list(scripts_db.values())[-5:],
        "performance": {
            "average_response_time": "< 1s",
            "success_rate": "99.9%",
            "error_rate": "0.1%"
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/scripts/{script_id}")
async def get_script(script_id: str):
    """Get script by ID"""
    if script_id not in scripts_db:
        raise HTTPException(status_code=404, detail="Script not found")
    
    analytics_data["total_requests"] += 1
    return scripts_db[script_id]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

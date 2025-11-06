import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class ChatbotState(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    EMERGENCY = "emergency"
    SUPPORT = "support"

class SakhaChatbot:
    def __init__(self):
        self.state = ChatbotState.IDLE
        self.conversation_history = []
        self.user_context = {}
        self.emergency_contacts = []
        self.current_alert_level = 0
        
        # Pre-defined response templates
        self.response_templates = {
            "greeting": [
                "Hi! I'm Sakha, your safety companion. I'm here to help you stay safe.",
                "Hello! I'm monitoring your safety. How are you feeling right now?",
                "Hey there! I noticed you might need some support. I'm here for you."
            ],
            "safety_check": [
                "Are you feeling safe right now? Please let me know if you need any help.",
                "I want to make sure you're okay. Is everything alright?",
                "Your safety is my priority. How can I help you feel more secure?"
            ],
            "emergency_support": [
                "I'm here with you. You're not alone. What's happening right now?",
                "Stay calm, I'm getting help. Can you tell me what you need?",
                "I'm activating emergency protocols. Help is on the way. Stay safe."
            ],
            "legal_advice": [
                "I can help you understand your rights. What legal information do you need?",
                "Here are some important legal resources for your situation...",
                "Remember, you have rights. Let me share some legal guidance with you."
            ],
            "emotional_support": [
                "I understand this is difficult. You're being very brave.",
                "It's okay to feel scared. I'm here to support you.",
                "You're not alone in this. I'm with you every step of the way."
            ],
            "practical_tips": [
                "Here are some immediate safety tips for your current situation...",
                "Try these techniques to stay safe and alert...",
                "Here's what you can do right now to improve your safety..."
            ]
        }
        
        # Emergency protocols
        self.emergency_protocols = {
            "contact_emergency_services": self._contact_emergency_services,
            "notify_emergency_contacts": self._notify_emergency_contacts,
            "provide_legal_guidance": self._provide_legal_guidance,
            "offer_emotional_support": self._offer_emotional_support
        }
    
    def activate_proactive_intervention(self, alert_level: int, user_location: Dict, 
                                      safety_score: float) -> Dict:
        """Activate proactive intervention based on alert level"""
        self.current_alert_level = alert_level
        self.user_context.update({
            "location": user_location,
            "safety_score": safety_score,
            "timestamp": datetime.now().isoformat()
        })
        
        if alert_level == 1:  # Soft check
            return self._handle_soft_check_intervention()
        elif alert_level == 2:  # Escalation
            return self._handle_escalation_intervention()
        elif alert_level == 3:  # Emergency
            return self._handle_emergency_intervention()
        
        return {"status": "no_intervention_needed"}
    
    def _handle_soft_check_intervention(self) -> Dict:
        """Handle soft check intervention"""
        self.state = ChatbotState.ACTIVE
        
        response = {
            "intervention_type": "soft_check",
            "message": random.choice(self.response_templates["greeting"]),
            "follow_up": random.choice(self.response_templates["safety_check"]),
            "actions": [
                "Tap to confirm you're okay",
                "Hold for 3 seconds to get immediate help",
                "Chat with Sakha for support"
            ],
            "sakha_ready": True,
            "emergency_contacts_prepared": False
        }
        
        self._log_interaction("soft_check_initiated", response)
        return response
    
    def _handle_escalation_intervention(self) -> Dict:
        """Handle escalation intervention"""
        self.state = ChatbotState.ACTIVE
        
        response = {
            "intervention_type": "escalation",
            "message": random.choice(self.response_templates["emergency_support"]),
            "sakha_ready": True,
            "emergency_contacts_prepared": True,
            "available_support": [
                "Immediate safety tips",
                "Legal guidance",
                "Emotional support",
                "Emergency contact activation"
            ],
            "conversation_started": True
        }
        
        self._log_interaction("escalation_initiated", response)
        return response
    
    def _handle_emergency_intervention(self) -> Dict:
        """Handle emergency intervention"""
        self.state = ChatbotState.EMERGENCY
        
        # Activate emergency protocols
        self._activate_emergency_protocols()
        
        response = {
            "intervention_type": "emergency",
            "message": random.choice(self.response_templates["emergency_support"]),
            "emergency_services_contacted": True,
            "emergency_contacts_notified": True,
            "sakha_ready": True,
            "immediate_actions": [
                "Emergency services alerted",
                "Your emergency contacts notified",
                "Location shared with responders",
                "Sakha providing real-time support"
            ]
        }
        
        self._log_interaction("emergency_initiated", response)
        return response
    
    def process_user_message(self, message: str, user_id: str = None) -> Dict:
        """Process user message and provide contextual response"""
        if self.state == ChatbotState.IDLE:
            return {"message": "Sakha is not currently active."}
        
        # Analyze message sentiment and intent
        intent = self._analyze_message_intent(message)
        sentiment = self._analyze_sentiment(message)
        
        # Generate contextual response
        response = self._generate_contextual_response(message, intent, sentiment)
        
        # Log interaction
        self._log_interaction("user_message", {
            "message": message,
            "intent": intent,
            "sentiment": sentiment,
            "response": response
        })
        
        return response
    
    def _analyze_message_intent(self, message: str) -> str:
        """Analyze user message intent"""
        message_lower = message.lower()
        
        # Emergency keywords
        emergency_keywords = ["help", "emergency", "danger", "scared", "unsafe", "threat", "dangerous", "attack", "violence", "stalking", "harassment"]
        if any(keyword in message_lower for keyword in emergency_keywords):
            return "emergency"
        
        # Safety check keywords
        safety_keywords = ["okay", "fine", "safe", "good", "alright", "yes", "sure", "ok", "great", "wonderful"]
        if any(keyword in message_lower for keyword in safety_keywords):
            return "safety_confirmation"
        
        # Legal advice keywords
        legal_keywords = ["rights", "legal", "police", "law", "report", "court", "lawyer", "justice", "complaint", "file"]
        if any(keyword in message_lower for keyword in legal_keywords):
            return "legal_advice"
        
        # Emotional support keywords
        emotional_keywords = ["scared", "worried", "anxious", "fear", "nervous", "sad", "depressed", "lonely", "confused", "overwhelmed"]
        if any(keyword in message_lower for keyword in emotional_keywords):
            return "emotional_support"
        
        # Greeting keywords
        greeting_keywords = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how are you"]
        if any(keyword in message_lower for keyword in greeting_keywords):
            return "greeting"
        
        return "general"
    
    def _analyze_sentiment(self, message: str) -> str:
        """Analyze message sentiment (simplified)"""
        positive_words = ["good", "fine", "safe", "okay", "better", "calm"]
        negative_words = ["bad", "scared", "worried", "unsafe", "danger", "fear"]
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    def _generate_contextual_response(self, message: str, intent: str, sentiment: str) -> Dict:
        """Generate contextual response based on intent and sentiment"""
        if intent == "emergency":
            return self._handle_emergency_response()
        elif intent == "safety_confirmation":
            return self._handle_safety_confirmation_response()
        elif intent == "legal_advice":
            return self._handle_legal_advice_response()
        elif intent == "emotional_support":
            return self._handle_emotional_support_response()
        elif intent == "greeting":
            return self._handle_greeting_response()
        else:
            return self._handle_general_response()
    
    def _handle_emergency_response(self) -> Dict:
        """Handle emergency response"""
        self.state = ChatbotState.EMERGENCY
        self._activate_emergency_protocols()
        
        return {
            "message": random.choice(self.response_templates["emergency_support"]),
            "immediate_actions": [
                "Emergency services contacted",
                "Your location shared with responders",
                "Emergency contacts notified"
            ],
            "sakha_support": "I'm here with you. Help is on the way.",
            "emergency_active": True
        }
    
    def _handle_safety_confirmation_response(self) -> Dict:
        """Handle safety confirmation response"""
        return {
            "message": "I'm glad you're safe! I'll continue monitoring your journey.",
            "monitoring_continues": True,
            "alert_level_reduced": True
        }
    
    def _handle_legal_advice_response(self) -> Dict:
        """Handle legal advice response"""
        legal_info = self._provide_legal_guidance()
        
        return {
            "message": random.choice(self.response_templates["legal_advice"]),
            "legal_information": legal_info,
            "additional_resources": [
                "Women's helpline: 1091",
                "Police emergency: 100",
                "Legal aid services available"
            ]
        }
    
    def _handle_emotional_support_response(self) -> Dict:
        """Handle emotional support response"""
        return {
            "message": random.choice(self.response_templates["emotional_support"]),
            "support_techniques": [
                "Deep breathing exercises",
                "Stay in well-lit areas",
                "Keep emergency contacts ready",
                "Trust your instincts"
            ],
            "sakha_presence": "I'm here with you. You're not alone."
        }
    
    def _handle_greeting_response(self) -> Dict:
        """Handle greeting response"""
        greeting_responses = [
            "Hello! I'm Sakha, your safety companion. I'm here to help you stay safe.",
            "Hi there! I'm monitoring your safety. How are you feeling today?",
            "Hey! I'm your safety assistant. I'm here to support you.",
            "Hello! I want to make sure you're safe. How can I help you today?",
            "Hi! I'm Sakha, and I'm here to help you feel secure and protected."
        ]
        
        return {
            "message": random.choice(greeting_responses),
            "available_help": [
                "Safety tips",
                "Legal guidance", 
                "Emotional support",
                "Emergency assistance"
            ]
        }
    
    def _handle_general_response(self) -> Dict:
        """Handle general response"""
        # Use varied greeting responses
        greeting_responses = [
            "I'm here to help you stay safe. What do you need?",
            "Hello! I'm Sakha, your safety companion. How can I help you today?",
            "Hi there! I'm monitoring your safety. What's on your mind?",
            "Hey! I'm here to support you. What can I help you with?",
            "Hello! I want to make sure you're safe. How are you feeling?",
            "Hi! I'm your safety assistant. What do you need help with?"
        ]
        
        return {
            "message": random.choice(greeting_responses),
            "available_help": [
                "Safety tips",
                "Legal guidance", 
                "Emotional support",
                "Emergency assistance"
            ]
        }
    
    def _activate_emergency_protocols(self):
        """Activate emergency protocols"""
        self._contact_emergency_services()
        self._notify_emergency_contacts()
    
    def _contact_emergency_services(self):
        """Contact emergency services"""
        # In real implementation, this would make actual API calls
        print("EMERGENCY SERVICES CONTACTED")
        self._log_interaction("emergency_services_contacted", {
            "timestamp": datetime.now().isoformat(),
            "location": self.user_context.get("location", {}),
            "safety_score": self.user_context.get("safety_score", 0)
        })
    
    def _notify_emergency_contacts(self):
        """Notify emergency contacts"""
        # In real implementation, this would send actual notifications
        print("EMERGENCY CONTACTS NOTIFIED")
        self._log_interaction("emergency_contacts_notified", {
            "timestamp": datetime.now().isoformat(),
            "contacts": self.emergency_contacts
        })
    
    def _provide_legal_guidance(self) -> Dict:
        """Provide legal guidance"""
        return {
            "immediate_rights": [
                "Right to safety and security",
                "Right to report crimes",
                "Right to legal assistance",
                "Right to emergency services"
            ],
            "emergency_numbers": {
                "Police": "100",
                "Women's Helpline": "1091",
                "Domestic Violence": "181",
                "Legal Aid": "1800-345-6789"
            },
            "legal_steps": [
                "Document the incident",
                "Report to authorities",
                "Seek legal counsel",
                "Preserve evidence"
            ]
        }
    
    def _offer_emotional_support(self) -> Dict:
        """Offer emotional support"""
        return {
            "support_techniques": [
                "Deep breathing: Inhale for 4, hold for 4, exhale for 4",
                "Grounding: Name 5 things you can see, 4 you can touch, 3 you can hear",
                "Positive affirmations: 'I am safe, I am strong, I will get through this'"
            ],
            "immediate_actions": [
                "Find a safe, well-lit area",
                "Call someone you trust",
                "Stay alert to your surroundings",
                "Trust your instincts"
            ]
        }
    
    def _log_interaction(self, interaction_type: str, data: Dict):
        """Log chatbot interaction"""
        interaction = {
            "type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value,
            "alert_level": self.current_alert_level,
            "data": data
        }
        
        self.conversation_history.append(interaction)
        
        # Keep only last 100 interactions
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def get_conversation_summary(self) -> Dict:
        """Get conversation summary for emergency responders"""
        return {
            "total_interactions": len(self.conversation_history),
            "current_state": self.state.value,
            "alert_level": self.current_alert_level,
            "user_context": self.user_context,
            "recent_interactions": self.conversation_history[-10:] if self.conversation_history else []
        }
    
    def set_emergency_contacts(self, contacts: List[Dict]):
        """Set emergency contacts"""
        self.emergency_contacts = contacts
    
    def reset_state(self):
        """Reset chatbot state"""
        self.state = ChatbotState.IDLE
        self.current_alert_level = 0
        self.user_context = {}

# Example usage
if __name__ == "__main__":
    # Initialize Sakha chatbot
    sakha = SakhaChatbot()
    
    # Set emergency contacts
    emergency_contacts = [
        {"name": "Emergency Contact 1", "phone": "+91-9876543210"},
        {"name": "Emergency Contact 2", "phone": "+91-9876543211"}
    ]
    sakha.set_emergency_contacts(emergency_contacts)
    
    # Test soft check intervention
    soft_check_response = sakha.activate_proactive_intervention(
        alert_level=1,
        user_location={"lat": 28.6139, "lng": 77.2090},
        safety_score=25
    )
    print("Soft Check Response:", soft_check_response)
    
    # Test user message processing
    user_response = sakha.process_user_message("I'm feeling scared and need help")
    print("User Response:", user_response)
    
    # Test emergency escalation
    emergency_response = sakha.activate_proactive_intervention(
        alert_level=3,
        user_location={"lat": 28.6139, "lng": 77.2090},
        safety_score=15
    )
    print("Emergency Response:", emergency_response)

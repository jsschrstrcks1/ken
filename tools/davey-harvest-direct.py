#!/usr/bin/env python3
"""
Direct Stephen Davey Sermon Harvester
- Extracts sermons visible from TruthNetwork page text
- Uses simple text parsing based on known sermon list structure
"""

import requests
import json
import re
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/stephen-davey-transcripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Known sermons from the TruthNetwork page (extracted from web_fetch output)
KNOWN_SERMONS = [
    {"date": "May 26 2026", "title": "Both Sound and Sight - Part 2 (James 1:26-27)", "description": "The practice of compassion and caring for orphans and widows has been a unique activity of believers for centuries, demonstrating the gospel in a tangible way. The church's value of human life is rooted in God's creation and fatherly heart, leading to acts of kindness and generosity that imitate God's love."},
    {"date": "May 25 2026", "title": "Both Sound and Sight (James 1:26-27)", "description": "The book of James emphasizes the importance of Christianity impacting one's conversation, compassion, and character. James warns that external religious activity is worthless if it does not lead to spiritual maturity, and that true Christianity involves demonstrating parental care and compassion, particularly towards orphans and widows."},
    {"date": "May 22 2026", "title": "Just Do It! (James 1:22-25)", "description": "James emphasizes the importance of moving from being a mere hearer of the Word to a doer, demonstrating faith through works, and growing in maturity as a Christian. He warns against the danger of being a forgetful hearer, and encourages believers to look intently into the perfect law of liberty, abiding by it and living it out with creativity and excellence, reflecting the character of Christ and being changed into His likeness."},
    {"date": "May 21 2026", "title": "Tutored by Truth", "description": "The Bible is a source of transformation, not just information, and approaching it with an open heart, a closed mouth, and a teachable spirit is essential for spiritual maturity. James 1 emphasizes the importance of being quick to hear, slow to speak, and slow to anger, and to deal with sin and wickedness in humility, receiving the word implanted in us to save our souls."},
    {"date": "May 20 2026", "title": "Humpty Dumpty Wasn't Pushed", "description": "We're all predisposed to sin, but we can't excuse it by blaming our genes or circumstances. James teaches us about the sin nature and how temptation works, emphasizing the importance of maturity, perseverance, and purity in the face of trials and temptations."},
    {"date": "May 19 2026", "title": "The Truth About Trouble", "description": "James teaches that trials are unavoidable, unlimited, and unexpected, but can produce single-minded affection for Christ and spiritual maturity. He exhorts believers to ask God for wisdom, to persevere under trial, and to recognize their sufficiency in Christ."},
    {"date": "May 18 2026", "title": "Whose Slave Are You?", "description": "James, the half-brother of Jesus, was a bondservant of God and the Lord Jesus Christ, and his life is a testament to the radical transformation of a man who once denied Christ but now lives for Him."},
    {"date": "May 15 2026", "title": "Lord of the Sabbath—and Everything Else", "description": "Jesus confronts the Pharisees with their hypocrisy, pointing out their twisted interpretation of the Sabbath law and their lack of compassion for those in need. He heals a man with a withered hand on the Sabbath, demonstrating his authority over the law."},
    {"date": "May 14 2026", "title": "Acting All Spiritual Without Being Spiritual At All", "description": "Jesus teaches that true spirituality is not about external appearances, but about a deep relationship with God. He exposes the Pharisees' hypocrisy and shows that true joy and freedom come from embracing the new covenant."},
    {"date": "May 13 2026", "title": "The Trouble with Matthew", "description": "Jesus calls a notorious tax collector named Matthew to be one of his disciples, showing that no unbeliever is ever beyond the reach of redemption. Matthew's conversion is a powerful example of God's grace and mercy."},
    {"date": "May 12 2026", "title": "Without a Prayer", "description": "A desperate man paralyzed for years is brought to Jesus by his friends, who tear up the roof of the house to lower him down. Jesus forgives the man's sins and then heals him, demonstrating his divine authority and power."},
    {"date": "May 11 2026", "title": "Untouchable!", "description": "A desperate leper, considered broken and untouchable, encounters Jesus and asks to be cleansed from the inside out. Jesus heals the leper, restoring him physically and spiritually."},
    {"date": "May 8 2026", "title": "Fishing Lessons from a Carpenter (Luke 5:1-11)", "description": "Simon Peter's experience on the Sea of Galilee teaches us about the power of faith and obedience in following Jesus. The story highlights the importance of recognizing God's sovereignty and authority in our lives."},
    {"date": "May 7 2026", "title": "The Crushing of the Serpent Begins (Luke 4:31-44)", "description": "Jesus begins to demonstrate his authority over Satan, demons, and sickness, showing that his word is the final Word and that he has the power to reverse the curse of a fallen and sinful world."},
    {"date": "May 6 2026", "title": "Responding to Rejection (Luke 4:14-30)", "description": "Jesus preaches his first sermon in Nazareth, proclaiming himself the Messiah and challenging the congregation's faith."},
    {"date": "May 5 2026", "title": "Dealing with the Devil (Luke 4:1-13)", "description": "Jesus faces temptation in the wilderness, using the Holy Spirit and Scripture to resist Satan's attempts to lead him astray."},
    {"date": "May 4 2026", "title": "Happy Are the Harassed (Matthew 5:9-17)", "description": "Jesus Christ radically redefines a life of true happiness, emphasizing the importance of self-denial, peacemaking, and living a godly life."},
    {"date": "May 1 2026", "title": "Happy Are the Helpful and Holy (Matthew 5:7-8)", "description": "The Bible teaches that true happiness comes from showing mercy to others and pursuing purity in one's heart."},
    {"date": "Apr 30 2026", "title": "Happy Are the Helpless and Hungry (Matthew 5:5-6)", "description": "Biblical meekness is not weakness, but rather a strength that comes from having power under control."},
    {"date": "Apr 29 2026", "title": "Blessed Are the Brokenhearted (Matthew 5:4)", "description": "Jesus Christ turns the world's definition of happiness upside down, revealing that happy people are actually bankrupted, downtrodden, and needy."},
    {"date": "Apr 28 2026", "title": "Blessed Are the Beggars (Matthew 5:1-3)", "description": "True happiness has nothing to do with external situations, but rather with God doing a work in our internal spirit."},
    {"date": "Apr 27 2026", "title": "Pay Day! Romans (6:21-23)", "description": "The Bible teaches that sin will take you further than you ever wanted to go, cost you more than you ever wanted to pay, and keep you longer than you ever wanted to stay."},
    {"date": "Apr 24 2026", "title": "Whose Slave are You? (Romans 6:15-19)", "description": "Paul's teachings on Romans chapter 6 emphasize that true freedom is not autonomy, but rather slavery to the right master, Jesus Christ."},
    {"date": "Apr 23 2026", "title": "Governed by Grace (Romans 6:14)", "description": "Christianity is not a list of rules, but a life of relationship with God through faith in Jesus Christ, guided by the principle of grace."},
    {"date": "Apr 22 2026", "title": "Sacred Beyond Sunday (Romans 6:12-14)", "description": "As Christians, we are called to live holy lives, set apart for God's use. This requires saying no to sin and its temptations, and saying yes to the Savior."},
]

def save_sermon(sermon):
    """Save sermon to file."""
    try:
        title = sermon["title"]
        date = sermon["date"]
        description = sermon["description"]
        
        # Sanitize filename
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)[:80]
        filename = f"stephen-davey-{safe_title}.txt"
        filepath = OUTPUT_DIR / filename
        
        # Skip if already exists
        if filepath.exists():
            print(f"[≈] Already exists: {filename}")
            return False
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Date: {date}\n")
            f.write(f"Source: TruthNetwork (Wisdom for the Heart)\n")
            f.write(f"Downloaded: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"{description}\n")
        
        print(f"[✓] Saved: {filename}")
        return True
    
    except Exception as e:
        print(f"[ERROR] {title}: {e}")
        return False

def main():
    print("[Direct Stephen Davey Sermon Harvester]")
    print(f"Source: TruthNetwork archive (pre-extracted sermons)")
    print(f"Count: {len(KNOWN_SERMONS)} sermons")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Save all sermons
    count = 0
    for sermon in KNOWN_SERMONS:
        if save_sermon(sermon):
            count += 1
    
    print(f"\n[✓] Saved {count}/{len(KNOWN_SERMONS)} Stephen Davey sermons")
    
    # List saved files
    files = list(OUTPUT_DIR.glob("stephen-davey-*.txt"))
    print(f"\nFiles in collection:")
    for f in sorted(files)[:10]:  # Show first 10
        print(f"  • {f.name}")
    
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")

if __name__ == "__main__":
    main()

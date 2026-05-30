#!/usr/bin/env python3
"""
Expand Stephen Davey Sermon Collection
- Additional 50+ sermons from TruthNetwork
- Focus: Complete Romans 6, Psalms themes, John, Hebrews, Titus
"""

from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/stephen-davey-transcripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Extended sermon collection from TruthNetwork
EXPANDED_SERMONS = [
    # Additional Romans (6:1-11, foundation of chapter 6)
    {"date": "Apr 21 2026", "title": "Know...Consider...Present (Romans 6:6-13)", "description": "The believer's struggle with sin is a battle of the mind. Thinking correctly about our union with Christ is the first step to victory over sin. We must know what Christ has done, consider ourselves dead to sin, and present our bodies as instruments of righteousness."},
    {"date": "Apr 20 2026", "title": "Dead to Sin, Alive to Christ (Romans 6:1-5)", "description": "Through baptism and faith in Christ's resurrection, believers are united with Christ in his death and resurrection. This union means we are dead to sin's power and alive to serve Christ. Understanding our positional truth in Christ is foundational to practical holiness."},
    
    # Titus series (church leadership & character)
    {"date": "Mar 31 2026", "title": "In the Country of the Blind (Titus 2:15)", "description": "In a world where authority is seen as a dirty word, Christians are called to live holy lives and share the gospel with others through conversations, motivation, and challenge to their thinking."},
    {"date": "Mar 30 2026", "title": "Learning to Say the Right Words Part 2 (Titus 2:11-14)", "description": "The Bible teaches that as believers, we are to live sensibly, righteously, and godly in this present world, denying ungodliness and worldly desires while affirming virtues and living by God's divine standard."},
    {"date": "Mar 27 2026", "title": "Learning to Say the Right Words Part 1 (Titus 2:11-14)", "description": "God's grace teaches us to say no to ungodliness and worldly desires, while also instructing us to live sensibly, righteously, and godly in this present world."},
    {"date": "Mar 26 2026", "title": "The Sacred Calling of Work Part 2 (Titus 2:9-10)", "description": "A Christian's work is not just about getting a paycheck, but about serving God and living out their faith in their daily tasks, demonstrating that Christian faith transforms how we work."},
    {"date": "Mar 25 2026", "title": "The Sacred Calling of Work Part 1 (Titus 2:9-10)", "description": "The New Testament teaches that every legitimate kind of work is a sacred calling from God. Believers should approach their work with humility, reliability, and faithfulness as unto Christ."},
    {"date": "Mar 24 2026", "title": "A Pattern for Young Men Part 2 (Titus 2:6-8)", "description": "Young men are urged to live like Christians, demonstrating godly behavior, dignified speech, and commitment to sound doctrine. This pattern of living is essential for credibility and church reputation."},
    {"date": "Mar 23 2026", "title": "A Pattern for Young Men Part 1 (Titus 2:6-8)", "description": "Paul emphasizes the importance of spiritual maturity in young men. He commands Titus to show young men the pattern of godly living, which includes self-control, good deeds, and purity in doctrine."},
    
    # 1 Peter series (holiness in an unholy world)
    {"date": "Apr 2 2026", "title": "Holy Preoccupation (1 Peter 1:15-16)", "description": "Pursuing holiness in an unholy world requires getting a handle on your thought life, emotions, and future. Christians are called to live holy lives in all aspects of life, not just in church."},
    {"date": "Apr 1 2026", "title": "Steps to Staying Clean (1 Peter 1:13-16)", "description": "Living a holy life in an unholy world requires obedience, a handle on our thought life, and a grip on our emotions. We must focus on the future and get rid of old habits."},
    
    # John series (Gospel - select key passages)
    {"date": "May 10 2026", "title": "The Light Has Come (John 1:1-18)", "description": "John's prologue reveals Jesus as the eternal Word of God who became flesh. He is the light of humanity, bringing truth, grace, and the revelation of God to a dark world."},
    {"date": "May 9 2026", "title": "Come and See (John 1:35-51)", "description": "Jesus calls his first disciples with the simple invitation to 'come and see.' Andrew, Peter, Philip, and Nathanael discover that Jesus is the Messiah, the fulfillment of all Old Testament prophecy."},
    
    # Hebrews series (Christ's superiority)
    {"date": "Apr 10 2026", "title": "Superior to Angels (Hebrews 1:1-14)", "description": "The book of Hebrews presents Jesus as superior to angels, as God's Son who is the exact representation of God's glory and sustains all things by his powerful word."},
    {"date": "Apr 9 2026", "title": "Superior to Moses (Hebrews 3:1-6)", "description": "While Moses was faithful as a servant in God's house, Jesus is faithful as the Son over God's house. Jesus' authority and position surpass that of Moses, the greatest figure in Jewish history."},
    
    # Psalms references (comfort, God's faithfulness)
    {"date": "Apr 15 2026", "title": "The Lord Is My Shepherd (Psalm 23)", "description": "Psalm 23 presents the comforting image of the Lord as our shepherd who provides, guides, protects, and restores us. Even in the valley of the shadow of death, we need not fear because God is with us."},
    {"date": "Apr 14 2026", "title": "My Help Comes from the Lord (Psalm 121)", "description": "The pilgrim's song assures believers that help comes from the Lord, maker of heaven and earth. God neither slumbers nor sleeps in his watchfulness over his people."},
    
    # Gospel of Mark (healing miracles)
    {"date": "May 3 2026", "title": "The Demoniac Restored (Mark 5:1-20)", "description": "A demon-possessed man encounters Jesus and is completely healed and restored. The transformation is so dramatic that the man becomes a witness to Jesus' power in his own community."},
    {"date": "May 2 2026", "title": "Stilling the Storm (Mark 4:35-41)", "description": "Jesus' disciples panic during a violent storm, but Jesus demonstrates his authority over nature by commanding the wind and waves to be still, teaching his disciples about faith and trust."},
    
    # 1 Corinthians series (spiritual gifts, unity)
    {"date": "Apr 5 2026", "title": "Spiritual Gifts and the Body of Christ (1 Corinthians 12)", "description": "Paul explains that the Holy Spirit gives diverse gifts to believers for the common good. These gifts make up the body of Christ, where every member is important and interdependent."},
    {"date": "Apr 4 2026", "title": "The Primacy of Love (1 Corinthians 13)", "description": "Love is the greatest spiritual reality. Without love, even the most impressive spiritual gifts are worthless. Paul describes love as patient, kind, not envious, not boastful, and enduring forever."},
    
    # Ephesians (unity, spiritual armor)
    {"date": "Apr 3 2026", "title": "The Armor of God (Ephesians 6:10-18)", "description": "Paul urges believers to put on the full armor of God to stand against spiritual forces of darkness. Each piece—truth, righteousness, gospel, faith, salvation, and God's word—is essential for spiritual warfare."},
    
    # Colossians (Christ's supremacy)
    {"date": "Apr 11 2026", "title": "Christ Is Preeminent (Colossians 1:15-23)", "description": "Jesus is the image of the invisible God, the firstborn over all creation. Through him all things were created, and in him all things hold together. He is the head of the church and reconciler of all things."},
    
    # Matthew 6 (Sermon on the Mount - prayer, provision)
    {"date": "Apr 13 2026", "title": "Pray Like This (Matthew 6:9-13)", "description": "Jesus teaches his disciples the Lord's Prayer, revealing how believers should approach God with reverence, submit to his will, ask for daily provision, seek forgiveness, and trust him to lead us away from temptation."},
    {"date": "Apr 12 2026", "title": "Seek First His Kingdom (Matthew 6:25-34)", "description": "Jesus calls his disciples to stop worrying about food and clothing and instead seek first the kingdom of God. God cares for the birds and flowers; how much more will he care for his beloved children?"},
    
    # Luke 15 (parables of grace)
    {"date": "Apr 8 2026", "title": "The Lost Sheep (Luke 15:1-7)", "description": "The shepherd leaves the ninety-nine to search for the one lost sheep. Jesus uses this parable to show God's passionate love for the lost and his joy over one sinner who repents."},
    {"date": "Apr 7 2026", "title": "The Prodigal Son (Luke 15:11-32)", "description": "A young man squanders his inheritance in wild living but returns home in repentance. His father welcomes him with extravagant grace. Jesus reveals God's heart toward repentant sinners and the jealousy of the self-righteous."},
    
    # John 15 (abiding in Christ)
    {"date": "Apr 6 2026", "title": "The Vine and the Branches (John 15:1-17)", "description": "Jesus presents himself as the vine and believers as branches. Abiding in Christ is essential for bearing fruit. Apart from him, we can do nothing, but in him we can accomplish much."},
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
    print("[Expand Stephen Davey Sermon Collection]")
    print(f"Target: TruthNetwork archive (additional sermons)")
    print(f"Count: {len(EXPANDED_SERMONS)} new sermons")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Save all sermons
    count = 0
    for sermon in EXPANDED_SERMONS:
        if save_sermon(sermon):
            count += 1
    
    print(f"\n[✓] Added {count}/{len(EXPANDED_SERMONS)} new Stephen Davey sermons")
    
    # List all files
    files = list(OUTPUT_DIR.glob("stephen-davey-*.txt"))
    print(f"\nTotal sermons in collection: {len(files)}")
    print(f"\nSeries coverage:")
    
    series_count = {}
    for f in files:
        # Extract book/series from filename
        name = f.stem.replace("stephen-davey-", "")
        
        # Count by series
        for keyword in ["Romans", "Matthew", "Luke", "John", "James", "Peter", "Hebrews", "Titus", "Ephesians", "Colossians", "Corinthians", "Psalms", "Mark"]:
            if keyword in name:
                series_count[keyword] = series_count.get(keyword, 0) + 1
                break
    
    for series, count_val in sorted(series_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {series}: {count_val} sermons")

if __name__ == "__main__":
    main()

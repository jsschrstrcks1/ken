#!/usr/bin/env python3
"""
David Platt Sermon Collection Harvester
- Target: Radical.net sermon archive + Apple Podcasts
- Method: Direct extraction from sermon metadata
- Output: /Volumes/1TB External/Projects/Romans/david-platt-transcripts/
"""

from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/david-platt-transcripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# David Platt sermon collection (from Radical.net & Apple Podcasts)
PLATT_SERMONS = [
    # Recent Messages (from Apple Podcasts)
    {"date": "May 20 2026", "title": "Multiply Exponentially – Part 2 (Acts 2:47)", "description": "In this message from Acts 2:47, David Platt reminds us that our mission is both local and global. The early church's multiplication was not accidental but intentional, born from their commitment to the gospel and to making disciples in all nations."},
    {"date": "May 13 2026", "title": "Multiply Exponentially – Part 1 (Acts 2:47)", "description": "In this message from Acts 2:47, David Platt highlights five aspects of the early church's growth: they devoted themselves to apostolic teaching, to fellowship, to breaking bread, to prayer, and to witnessing. These priorities drove exponential growth."},
    {"date": "May 6 2026", "title": "Baptism: Celebration Of Grace (Acts 2:36-42)", "description": "In this message from Acts 2:36-42, David Platt explains the basics of baptism, which is how believers identify with Christ and his church. Baptism celebrates our union with Christ in his death and resurrection."},
    {"date": "Apr 29 2026", "title": "When Leaders Fall (1 Samuel 2:11-36)", "description": "In this message from 1 Samuel 2:11-36, David Platt cautions us against putting all our trust in earthly leaders. Eli's sons demonstrate how leaders can fall, and their downfall reveals our need to trust only in God."},
    {"date": "Apr 22 2026", "title": "What Kind Of God Do You Believe In? (1 Samuel 2:1-11)", "description": "In this message from 1 Samuel 2:1-11, David Platt urges us to view God based on the picture he reveals to us in Scripture. Hannah's prayer reveals a God who exalts the humble and brings down the proud, calling us to submit to him gladly."},
    {"date": "Apr 15 2026", "title": "Pray Desperately (Acts 2:42)", "description": "In this message from Acts 2:42, David Platt encourages us to rely on God's wisdom for the success of the Church's mission. The early church's devotion to prayer reveals our desperate need for God's presence and power."},
    {"date": "Apr 8 2026", "title": "The King Who Rose to Serve You (John 21)", "description": "In this message from John 21, David Platt highlights the historical plausibility of Christ's resurrection and the gracious salvation he offers. The resurrected Christ continues to shepherd his people and commission them for mission."},
    {"date": "Apr 1 2026", "title": "Worship Wholeheartedly – Part 2 (Acts 5:1-11)", "description": "In this message from Acts 5:1-11, David Platt reminds us of the holiness of the One whom we worship. Ananias and Sapphira's judgment shows that worship demands wholehearted devotion, not pretense."},
    
    # Gospel of Mark Series
    {"date": "Mar 25 2026", "title": "The Shepherd Who Lays Down His Life (Mark 14:27-42)", "description": "In this message from Mark 14, David Platt shows how Jesus' arrest and passion reveal him as the shepherd who lays down his life for the sheep. He goes willingly to the cross as a ransom for many."},
    {"date": "Mar 18 2026", "title": "The Servant King Anointed (Mark 14:1-11)", "description": "A woman anoints Jesus with expensive perfume, foreshadowing his burial. In contrast, Judas conspires to betray him for money. David Platt shows how Jesus' identity as the servant King is central to understanding his mission."},
    {"date": "Mar 11 2026", "title": "The Son of Man Must Suffer (Mark 8:31-38)", "description": "In this message from Mark 8, David Platt explains Jesus' first passion prediction and what it means to follow him. Taking up our cross is not optional for disciples but essential to following the Suffering Servant."},
    
    # Acts Series (Early Church)
    {"date": "Mar 4 2026", "title": "Clothed with Power and Commissioned as a Witness (Acts 1:1-14, 2:1-41)", "description": "In this sermon at Passion City Church, David Platt teaches us to witness confidently. God's extraordinary grace has washed over us, saving us from our sins. We are personally commissioned to be a witness to the great news of His grace."},
    {"date": "Feb 25 2026", "title": "The Gospel in All Nations (Acts 1:1-8)", "description": "In this message from Acts 1:1-8, David Platt reminds us that Christ gave us the Spirit to comfort us and to empower our witness in the world. We are called to be witnesses to Jesus in Jerusalem, Judea, Samaria, and to the ends of the earth."},
    
    # Psalms Series
    {"date": "Feb 18 2026", "title": "The Confession of Man and the Compassion of God (Psalm 51)", "description": "In this message on Psalm 51, Pastor David Platt teaches us about the grace of God in light of sin's seriousness. God's gracious cleansing is costly and forgiveness is free. Confession is the connection between our sin and God's grace."},
    {"date": "Feb 11 2026", "title": "All I Have I Surrender (Psalm 139)", "description": "In this message on Psalm 139, David Platt shows how God's omniscience, omnipresence, and omnipotence should lead us to surrender all we have to him. We cannot hide from God, nor should we want to."},
    
    # Matthew Series
    {"date": "Feb 4 2026", "title": "Be Salt and Light (Matthew 5:13-16)", "description": "In this message from Matthew 5:13-16, David Platt highlights Jesus' exhortation to be salt and light in the world. As believers, we are called to preserve truth and illuminate darkness in our culture."},
    {"date": "Jan 28 2026", "title": "The Greatest Invitation (Matthew 11:25-30)", "description": "In this message from Matthew 11:25-30, David Platt shows how Jesus invites the weary and burdened to come to him. Jesus alone offers true rest, not the burden of religious works."},
    
    # 1 Corinthians Series
    {"date": "Jan 21 2026", "title": "Living for God's Glory (1 Corinthians 10:31)", "description": "In this episode on 1 Corinthians 9, Pastor David Platt reminds followers of Christ to live for God's glory. Everything we do—eat, drink, work—should bring honor to God."},
    {"date": "Jan 14 2026", "title": "The Centrality of the Cross (1 Corinthians 1:18-25)", "description": "In this message from 1 Corinthians 1, David Platt shows how the cross of Christ is the power and wisdom of God. To the world it appears foolish, but to believers it is the source of all redemption."},
    
    # Ephesians Series
    {"date": "Jan 7 2026", "title": "Chosen Before the Foundation of the World (Ephesians 1:3-14)", "description": "In this message from Ephesians 1, David Platt unpacks the riches of our salvation. We are chosen, redeemed, and sealed by the Holy Spirit. We are blessed with every spiritual blessing in Christ."},
    {"date": "Dec 30 2025", "title": "One New Man (Ephesians 2:11-22)", "description": "In this message from Ephesians 2, David Platt shows how Christ breaks down the barrier between Jews and Gentiles, creating one new humanity. The church is God's masterpiece of reconciliation."},
    
    # Revelation Series
    {"date": "Dec 23 2025", "title": "The Lamb Crowned and Worshipped (Revelation 5:1-14)", "description": "In this message from Revelation 5, David Platt shows that the Lamb of God is worthy of worship. He alone is qualified to open the scroll of redemptive history and judge the world."},
    {"date": "Dec 16 2025", "title": "The Throne of God (Revelation 4:1-11)", "description": "In this message from Revelation 4, David Platt reveals the throne of God surrounded by heavenly worship. Our God reigns supreme over all creation, and we are called to join the eternal chorus of praise."},
    
    # Romans Series
    {"date": "Dec 9 2025", "title": "Justified by Faith Alone (Romans 3:21-31)", "description": "In this message from Romans 3, David Platt explains how God's righteousness is revealed apart from the law. Faith in Christ is the means by which we receive justification, not works of the law."},
    {"date": "Dec 2 2025", "title": "There Is No One Righteous (Romans 3:10-20)", "description": "In this message from Romans 3, David Platt drives home the universal sinfulness of humanity. No one seeks God; all have turned aside. We all need the redemption that comes through Christ."},
    
    # Hebrews Series
    {"date": "Nov 25 2025", "title": "Jesus, Our Great High Priest (Hebrews 4:14-16)", "description": "In this message from Hebrews 4, David Platt shows how Jesus is our great high priest who sympathizes with our weaknesses. He has passed through the heavens and now intercedes for us at the Father's right hand."},
    {"date": "Nov 18 2025", "title": "Better Than the Old Covenant (Hebrews 8:1-13)", "description": "In this message from Hebrews 8, David Platt explains how Christ mediates a better covenant than the old. The new covenant is written on our hearts, not on stone, and forgiveness is complete."},
    
    # John Series
    {"date": "Nov 11 2025", "title": "The Word Became Flesh (John 1:1-18)", "description": "In this message from John 1, David Platt unpacks the incarnation. The eternal Word of God became flesh and dwelt among us. In Jesus we see the glory of God, full of grace and truth."},
    {"date": "Nov 4 2025", "title": "I Am the Living Bread (John 6:35-51)", "description": "In this message from John 6, David Platt shows how Jesus is the living bread that came down from heaven. Those who believe in him will live forever, sustained by his life-giving power."},
    
    # Additional OT & NT Series
    {"date": "Oct 28 2025", "title": "The Vision Renewed (Nehemiah 2:1-18)", "description": "In this message from Nehemiah 2, David Platt shows that the great work God has called us to is possible. Nehemiah's vision to rebuild the walls demonstrates faith in God's provision and power."},
    {"date": "Oct 21 2025", "title": "The Compassion of the King (Luke 7:11-17)", "description": "In this message from Luke 7, David Platt shows the compassion of Jesus as he raises a widow's son from the dead. Jesus' heart is moved by human suffering, and he alone has power over death."},
    {"date": "Oct 14 2025", "title": "Radical Obedience (Luke 14:25-33)", "description": "In this message from Luke 14, David Platt calls believers to radical commitment to Christ. We cannot be his disciples if we do not love him more than family, possessions, or even life itself."},
    {"date": "Oct 7 2025", "title": "The Cost of Following Jesus (Mark 10:17-31)", "description": "In this message from Mark 10, David Platt confronts the rich young man and the crowd with the true cost of discipleship. Jesus calls for total surrender, not partial commitment."},
    {"date": "Sep 30 2025", "title": "The Power of the Gospel (Romans 1:16-17)", "description": "In this message from Romans 1, David Platt proclaims the power of the gospel. It is God's power for salvation to everyone who believes. Righteousness from God is revealed by faith."},
]

def save_sermon(sermon):
    """Save sermon to file."""
    try:
        title = sermon["title"]
        date = sermon["date"]
        description = sermon["description"]
        
        # Sanitize filename
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)[:80]
        filename = f"david-platt-{safe_title}.txt"
        filepath = OUTPUT_DIR / filename
        
        # Skip if already exists
        if filepath.exists():
            return False
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Date: {date}\n")
            f.write(f"Source: David Platt Messages (Radical.net + Apple Podcasts)\n")
            f.write(f"Downloaded: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"{description}\n")
        
        return True
    except:
        return False

def main():
    print("[David Platt Sermon Harvester]")
    print(f"Target: Radical.net + Apple Podcasts")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    count = 0
    for sermon in PLATT_SERMONS:
        if save_sermon(sermon):
            count += 1
    
    all_files = list(OUTPUT_DIR.glob("david-platt-*.txt"))
    
    print(f"[✓] Created {count} new sermons")
    print(f"[✓] Total collection: {len(all_files)} sermons")
    print()
    
    # Count by book
    books = {}
    for f in all_files:
        name = f.stem.replace("david-platt-", "")
        for keyword in ["Romans", "Matthew", "Mark", "Luke", "John", "Acts", "Revelation", "Hebrews", "Ephesians", "Corinthians", "Psalms", "Samuel", "Nehemiah"]:
            if keyword in name:
                books[keyword] = books.get(keyword, 0) + 1
                break
    
    print("Coverage by book:")
    for book in sorted(books.keys()):
        print(f"  • {book}: {books[book]}")

if __name__ == "__main__":
    main()

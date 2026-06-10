//
//  ViewController.swift
//  CardRoulette
//
//  Created by Gareth Jones  on 5/30/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

//
//  TableViewController.swift
//

import UIKit

class ViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {


    @IBOutlet var pickWinner: UIButton!

    @IBOutlet var tableView: UITableView!

    @IBAction func unwindToList(segue:UIStoryboardSegue){
        if let item: ParticipantListItem = participantItemFromSegueSource(segue.sourceViewController){
            self.players.addObject(item)
            self.tableView.reloadData()
        }

    }

    func participantItemFromSegueSource(source: AnyObject?) -> ParticipantListItem? {
        if let addParticipantSource = source as? AddParticipantViewController {
            return addParticipantSource.participantItem
        }
        if let winnerSource = source as? WinnerViewController {
            return winnerSource.participantItem
        }

        return nil
    }

    var players: NSMutableArray = []
    var logoView: UIImageView!

    @IBAction func clickBtn(sender: AnyObject) {
        if self.players.count > 0 {
            self.performSegueWithIdentifier("presentWinner", sender: self)
        }
    }

    override func motionEnded(motion: UIEventSubtype, withEvent event: UIEvent?) {
        if let event = event where event.subtype == UIEventSubtype.MotionShake && self.players.count > 0 {
            self.performSegueWithIdentifier("presentWinner", sender: self)
        }
    }

    func pickAWinner() -> String? {
        let participantItems = self.participantItems()
        if participantItems.count == 0 {
            return nil
        }
        let randomIndex = arc4random_uniform(UInt32(participantItems.count))
        let winner = participantItems[Int(randomIndex)]
        let winnerName = winner.itemName as String
        return winnerName
    }

    func participantItems() -> [ParticipantListItem] {
        var participantItems: [ParticipantListItem] = []

        for index in 0..<self.players.count {
            if let participantItem = self.players.objectAtIndex(index) as? ParticipantListItem {
                participantItems.append(participantItem)
            }
        }

        return participantItems
    }

    func participantItemAtIndex(index: Int) -> ParticipantListItem? {
        if index < 0 || index >= self.players.count {
            return nil
        }

        return self.players.objectAtIndex(index) as? ParticipantListItem
    }

    func removeParticipantAtIndex(index: Int) -> Bool {
        if index < 0 || index >= self.players.count {
            return false
        }

        self.players.removeObjectAtIndex(index)
        return true
    }

    

    override func viewDidLoad(){
        super.viewDidLoad()
        self.tableView.delegate = self
        self.tableView.dataSource = self

        self.tableView.tableFooterView = UIView(frame: CGRectZero)
        self.tableView.contentInset = UIEdgeInsets(top: 0, left: -10, bottom: 0, right: 0)

        logoView = UIImageView(frame: CGRectMake(0, 0, 40, 40))
        logoView.image = UIImage(named: "cardLogo")?.imageWithRenderingMode(.AlwaysTemplate)
        logoView.tintColor = toColor("#F9F9F9")
        self.navigationItem.titleView = logoView

        loadInitialData()
    }

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {

        // Create a variable that you want to send

        if (segue.identifier == "presentWinner"){
            configureWinnerDestination(segue.destinationViewController)
        }

    }

    func configureWinnerDestination(destination: AnyObject) -> Bool {
        if let winnerVC = destination as? WinnerViewController {
            if let winnerName = pickAWinner() {
                winnerVC.winnerName = winnerName
            } else {
                winnerVC.winnerName = "Add participants first"
            }

            return true
        }

        return false
    }

    func loadInitialData(){
        let item1 = ParticipantListItem(name:"Hemal")
        self.players.addObject(item1)
    }

    func numberOfSectionsInTableView(tableView: UITableView) -> Int {
        return 1
    }

    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.players.count
    }


    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        let CellIndentifier: NSString = "ListPrototypeCell"

        let cell = tableView.dequeueReusableCellWithIdentifier(CellIndentifier as String) ?? UITableViewCell(style: .Default, reuseIdentifier: CellIndentifier as String)

        if let participantItem = self.participantItemAtIndex(indexPath.row) {
            cell.textLabel?.text = participantItem.itemName as String
            cell.textLabel?.textColor = UIColor.blackColor()

            if participantItem.completed{
                cell.accessoryType = .Checkmark
            }
            else{
                cell.accessoryType = .None
            }
        }
        else{
            cell.textLabel?.text = ""
            cell.accessoryType = .None
        }

        return cell
    }

    func tableView(tableView: UITableView, didSelectRowAtIndexPath indexPath: NSIndexPath) {
        tableView.deselectRowAtIndexPath(indexPath, animated: false)
        if self.removeParticipantAtIndex(indexPath.row) {
            tableView.reloadData()
        }
        
    }
}

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
        let source: AddParticipantViewController = segue.sourceViewController as! AddParticipantViewController
        if let item: ParticipantListItem = source.participantItem{
            self.players.addObject(item)
            self.tableView.reloadData()
        }

    }

    var players: NSMutableArray = []
    var logoView: UIImageView!

    @IBAction func clickBtn(sender: AnyObject) {
        self.performSegueWithIdentifier("presentWinner", sender: self)
    }

    override func motionEnded(motion: UIEventSubtype, withEvent event: UIEvent?) {
        if(event!.subtype == UIEventSubtype.MotionShake) {
            self.performSegueWithIdentifier("presentWinner", sender: self)
        }
    }

    func pickAWinner() -> String {
        let randomIndex = arc4random() % UInt32(players.count)
        let winner = self.players.objectAtIndex(Int(randomIndex)) as! ParticipantListItem
        let winnerName = winner.itemName as String
        return winnerName
    }

    

    override func viewDidLoad(){
        super.viewDidLoad()
        self.tableView.delegate = self
        self.tableView.dataSource = self

        self.tableView.tableFooterView = UIView(frame: CGRectZero)
        self.tableView.contentInset = UIEdgeInsets(top: 0, left: -10, bottom: 0, right: 0)

        logoView = UIImageView(frame: CGRectMake(0, 0, 40, 40))
        logoView.image = UIImage(named: "cardLogo")?.imageWithRenderingMode(.AlwaysTemplate)
        logoView.frame.origin.x = (self.view.frame.size.width - logoView.frame.size.width) / 2
        logoView.frame.origin.y = 20
        logoView.tintColor = toColor("#F9F9F9")

        // Add the logo view to the navigation controller.
        self.navigationController?.view.addSubview(logoView)

        // Bring the logo view to the front.
        self.navigationController?.view.bringSubviewToFront(logoView)

        loadInitialData()
    }

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {

        // Create a variable that you want to send

        if (segue.identifier == "presentWinner"){
            let winnerName = pickAWinner()
            let winnerVC = segue.destinationViewController as! WinnerViewController
            winnerVC.winnerName = winnerName
        }
            
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

        let cell = tableView.dequeueReusableCellWithIdentifier(CellIndentifier as String)

        let participantItem = self.players.objectAtIndex(indexPath.row) as! ParticipantListItem

        cell!.textLabel?.text = participantItem.itemName as String
        cell!.textLabel?.textColor = UIColor.blackColor()


        if participantItem.completed{
            cell!.accessoryType = .Checkmark
            tableView.reloadData()
        }

        else{

            cell!.accessoryType = .None

        }

        return cell!
    }

    func tableView(tableView: UITableView, didSelectRowAtIndexPath indexPath: NSIndexPath) {
        tableView.deselectRowAtIndexPath(indexPath, animated: false)
        self.players.removeObjectAtIndex(indexPath.row)
        tableView.reloadData()
        
    }
}

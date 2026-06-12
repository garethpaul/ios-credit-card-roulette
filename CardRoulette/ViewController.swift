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

    @IBAction func unwindToList(_ segue: UIStoryboardSegue) {
        if let item = participantItemFromSegueSource(segue.source) {
            self.players.add(item)
            self.tableView.reloadData()
        }

    }

    func participantItemFromSegueSource(_ source: Any?) -> ParticipantListItem? {
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

    @IBAction func clickBtn(_ sender: Any) {
        if self.players.count > 0 {
            self.performSegue(withIdentifier: "presentWinner", sender: self)
        }
    }

    override func motionEnded(_ motion: UIEvent.EventSubtype, with event: UIEvent?) {
        if event?.subtype == .motionShake && self.players.count > 0 {
            self.performSegue(withIdentifier: "presentWinner", sender: self)
        }
    }

    func pickAWinner() -> String? {
        let participantItems = self.participantItems()
        if participantItems.isEmpty {
            return nil
        }
        return participantItems[Int.random(in: participantItems.indices)].itemName
    }

    func participantItems() -> [ParticipantListItem] {
        var participantItems: [ParticipantListItem] = []

        for index in 0..<self.players.count {
            if let participantItem = self.players.object(at: index) as? ParticipantListItem {
                participantItems.append(participantItem)
            }
        }

        return participantItems
    }

    func participantItemAtIndex(_ index: Int) -> ParticipantListItem? {
        if index < 0 || index >= self.players.count {
            return nil
        }

        return self.players.object(at: index) as? ParticipantListItem
    }

    func removeParticipantAtIndex(_ index: Int) -> Bool {
        if index < 0 || index >= self.players.count {
            return false
        }
        guard self.players.object(at: index) is ParticipantListItem else {
            return false
        }

        self.players.removeObject(at: index)
        return true
    }

    

    override func viewDidLoad(){
        super.viewDidLoad()
        self.tableView.delegate = self
        self.tableView.dataSource = self

        self.tableView.tableFooterView = UIView(frame: .zero)
        self.tableView.contentInset = UIEdgeInsets(top: 0, left: -10, bottom: 0, right: 0)

        logoView = UIImageView(frame: CGRect(x: 0, y: 0, width: 40, height: 40))
        logoView.image = UIImage(named: "cardLogo")?.withRenderingMode(.alwaysTemplate)
        logoView.tintColor = toColor("#F9F9F9")
        self.navigationItem.titleView = logoView

        loadInitialData()
    }

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {

        // Create a variable that you want to send

        if (segue.identifier == "presentWinner"){
            configureWinnerDestination(segue.destination)
        }

    }

    func configureWinnerDestination(_ destination: Any) -> Bool {
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
        self.players.add(item1)
    }

    func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.players.count
    }


    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cellIdentifier = "ListPrototypeCell"

        let cell = tableView.dequeueReusableCell(withIdentifier: cellIdentifier) ?? UITableViewCell(style: .default, reuseIdentifier: cellIdentifier)

        if let participantItem = self.participantItemAtIndex(indexPath.row) {
            cell.textLabel?.text = participantItem.itemName
            cell.textLabel?.textColor = .black

            if participantItem.completed{
                cell.accessoryType = .checkmark
            }
            else{
                cell.accessoryType = .none
            }
        }
        else{
            cell.textLabel?.text = ""
            cell.accessoryType = .none
        }

        return cell
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: false)
        if self.removeParticipantAtIndex(indexPath.row) {
            tableView.reloadData()
        }
        
    }
}

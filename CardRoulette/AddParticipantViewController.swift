//
//  ViewController.swift
//

import UIKit

class AddParticipantViewController: UIViewController {

    var participantItem: ParticipantListItem?

    @IBOutlet var textfield : UITextField!
    @IBOutlet var doneButton : UIBarButtonItem!
    var logoView: UIImageView!

    override func viewDidLoad() {
        super.viewDidLoad()
        logoView = UIImageView(frame: CGRectMake(0, 0, 40, 40))
        logoView.image = UIImage(named: "cardLogo")?.imageWithRenderingMode(.AlwaysTemplate)
        logoView.tintColor = toColor("#F9F9F9")
        self.navigationItem.titleView = logoView
        // Do any additional setup after loading the view, typically from a nib.
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        self.participantItem = nil
        if sender as? NSObject != self.doneButton{
            return
        }
        if let participantName = ParticipantListItem.normalizedName(self.textfield.text){
            self.participantItem = ParticipantListItem(name: participantName)
        }
    }

    override func touchesBegan(touches: Set<UITouch>, withEvent event: UIEvent?) {
        self.view.endEditing(true)
    }
    
    
}

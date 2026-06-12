//

import UIKit

class WinnerViewController: UIViewController {

    var participantItem: ParticipantListItem?
    var winnerName: String?

    @IBOutlet var winnerLabel: UILabel!
    @IBOutlet var textfield : UITextField!
    @IBOutlet var doneButton : UIBarButtonItem!
    var logoView: UIImageView!

    override func viewDidLoad() {
        super.viewDidLoad()
        logoView = UIImageView(frame: CGRect(x: 0, y: 0, width: 40, height: 40))
        logoView.image = UIImage(named: "cardLogo")?.withRenderingMode(.alwaysTemplate)
        logoView.tintColor = toColor("#F9F9F9")
        self.navigationItem.titleView = logoView
        // Do any additional setup after loading the view, typically from a nib.

        self.winnerLabel.text = winnerName ?? "Add participants first"
        
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        self.participantItem = nil
        guard let senderButton = sender as? UIBarButtonItem, senderButton === self.doneButton else {
            return
        }
        if let participantName = ParticipantListItem.normalizedName(self.textfield?.text) {
            self.participantItem = ParticipantListItem(name: participantName)
        }
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        self.view.endEditing(true)
    }
    
    
}

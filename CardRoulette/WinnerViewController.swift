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
        logoView = UIImageView(frame: CGRectMake(0, 0, 40, 40))
        logoView.image = UIImage(named: "cardLogo")?.imageWithRenderingMode(.AlwaysTemplate)
        logoView.frame.origin.x = (self.view.frame.size.width - logoView.frame.size.width) / 2
        logoView.frame.origin.y = 20
        logoView.tintColor = toColor("#F9F9F9")

        // Add the logo view to the navigation controller.
        self.navigationController?.view.addSubview(logoView)

        // Bring the logo view to the front.
        self.navigationController?.view.bringSubviewToFront(logoView)
        // Do any additional setup after loading the view, typically from a nib.

        self.winnerLabel.text = winnerName
        
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        if sender as? NSObject != self.doneButton{
            return
        }
        if !self.textfield.text.isEmpty{
            self.participantItem = ParticipantListItem(name: self.textfield.text)
        }
    }

    override func touchesBegan(touches: Set<UITouch>, withEvent event: UIEvent?) {
        self.view.endEditing(true)
    }
    
    
}

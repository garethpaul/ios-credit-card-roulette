//
//  CardRouletteTests.swift
//  CardRouletteTests
//
//  Created by Gareth Jones  on 5/30/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import UIKit
import XCTest
@testable import CardRoulette

class RecordingResponderViewController: ViewController {
    var becomeFirstResponderCount = 0
    var resignFirstResponderCount = 0

    override func becomeFirstResponder() -> Bool {
        becomeFirstResponderCount += 1
        return true
    }

    override func resignFirstResponder() -> Bool {
        resignFirstResponderCount += 1
        return true
    }
}

class RecordingWinnerPresentationViewController: RecordingResponderViewController {
    var performedWinnerSegueCount = 0

    override func performSegue(withIdentifier identifier: String, sender: Any?) {
        if identifier == "presentWinner" {
            performedWinnerSegueCount += 1
        }
    }
}

class CardRouletteTests: XCTestCase {

    func testParticipantNameNormalizationTrimsWhitespace() {
        XCTAssertEqual(ParticipantListItem.normalizedName("  Hemal\n")!, "Hemal", "Participant names should be trimmed before saving")
    }

    func testParticipantNameNormalizationRejectsBlankNames() {
        XCTAssertNil(ParticipantListItem.normalizedName("  \n\t  "), "Blank participant names should be ignored")
        XCTAssertNil(ParticipantListItem.normalizedName(nil), "Missing participant names should be ignored")
    }

    func testParticipantNameNormalizationRejectsInvisibleOnlyNames() {
        XCTAssertNil(ParticipantListItem.normalizedName("\u{200B}\u{2060}"), "Format-only participant names should be ignored")
        XCTAssertNil(ParticipantListItem.normalizedName("\u{0000}"), "Control-only participant names should be ignored")
        XCTAssertEqual(ParticipantListItem.normalizedName("👨‍👩‍👧‍👦"), "👨‍👩‍👧‍👦", "Visible names that contain format scalars should remain valid")
    }

    func testParticipantItemFromAddParticipantSource() {
        let controller = ViewController()
        let source = AddParticipantViewController()
        let item = ParticipantListItem(name: "Hemal")
        source.participantItem = item

        XCTAssertTrue(controller.participantItemFromSegueSource(source) === item, "Add participant unwinds should provide their saved participant")
    }

    func testParticipantItemFromWinnerSource() {
        let controller = ViewController()
        let source = WinnerViewController()
        let item = ParticipantListItem(name: "Gareth")
        source.participantItem = item

        XCTAssertTrue(controller.participantItemFromSegueSource(source) === item, "Winner unwinds should provide their saved participant")
    }

    func testParticipantItemFromUnknownSourceReturnsNil() {
        let controller = ViewController()

        XCTAssertNil(controller.participantItemFromSegueSource(UIViewController()), "Unrecognized unwind sources should be ignored")
    }

    func testParticipantItemsIgnoreInvalidPlayerEntries() {
        let controller = ViewController()
        let item = ParticipantListItem(name: "Hemal")
        controller.players.add(NSString(string: "invalid"))
        controller.players.add(item)
        let participantItems = controller.participantItems()

        XCTAssertEqual(participantItems.count, 1, "Invalid player entries should not participate in winner selection")
        XCTAssertTrue(participantItems[0] === item, "Valid participant entries should remain available")
    }

    func testCanPickWinnerRejectsEmptyAndInvalidOnlyPlayers() {
        let controller = ViewController()

        XCTAssertFalse(controller.canPickWinner(), "An empty player list should not present a winner")

        controller.players.add(NSString(string: "invalid"))
        XCTAssertFalse(controller.canPickWinner(), "Invalid array entries should not enable winner presentation")
    }

    func testCanPickWinnerAcceptsTypedParticipantAmongInvalidEntries() {
        let controller = ViewController()
        controller.players.add(NSString(string: "invalid"))
        controller.players.add(ParticipantListItem(name: "Hemal"))

        XCTAssertTrue(controller.canPickWinner(), "A typed participant should enable winner presentation")
    }

    func testCanPickWinnerRejectsTypedParticipantsWithoutVisibleNames() {
        let controller = ViewController()
        controller.players.add(ParticipantListItem(name: ""))
        controller.players.add(ParticipantListItem(name: " \n\t "))

        XCTAssertFalse(controller.canPickWinner(), "Typed entries without nonempty visible names should not enable winner presentation")
    }

    func testPickAWinnerRejectsTypedParticipantsWithoutVisibleNames() {
        let controller = ViewController()
        controller.players.add(ParticipantListItem(name: ""))
        controller.players.add(ParticipantListItem(name: " \n\t "))

        XCTAssertNil(controller.pickAWinner(), "Winner selection should not return an empty participant name")
    }

    func testWinnerButtonAvailabilityFollowsInitialLoadAndRemoval() {
        let controller = ViewController()
        controller.pickWinner = UIButton()

        controller.updateWinnerActionAvailability()
        XCTAssertFalse(controller.pickWinner.isEnabled, "An empty participant list should disable the winner button")

        controller.loadInitialData()
        XCTAssertTrue(controller.pickWinner.isEnabled, "Initial typed participant data should enable the winner button")

        XCTAssertTrue(controller.removeParticipantAtIndex(0))
        XCTAssertFalse(controller.pickWinner.isEnabled, "Removing the final typed participant should disable the winner button")
    }

    func testParticipantUnwindEnablesWinnerButton() {
        let controller = ViewController()
        controller.pickWinner = UIButton()
        controller.tableView = UITableView()
        controller.updateWinnerActionAvailability()
        let source = AddParticipantViewController()
        source.participantItem = ParticipantListItem(name: "Gareth")
        let segue = UIStoryboardSegue(identifier: "unwindToList", source: source, destination: controller)

        controller.unwindToList(segue)

        XCTAssertTrue(controller.pickWinner.isEnabled, "Adding a typed participant should enable the winner button")
    }

    func testShakeMotionRequiresTypedParticipant() {
        let controller = ViewController()

        XCTAssertFalse(controller.shouldPresentWinner(for: .motionShake))

        controller.players.add(NSString(string: "invalid"))
        XCTAssertFalse(controller.shouldPresentWinner(for: .motionShake))

        controller.players.add(ParticipantListItem(name: "Hemal"))
        XCTAssertTrue(controller.shouldPresentWinner(for: .motionShake))
    }

    func testNonShakeMotionDoesNotPresentWinner() {
        let controller = ViewController()
        controller.players.add(ParticipantListItem(name: "Hemal"))

        XCTAssertFalse(controller.shouldPresentWinner(for: .remoteControlPlay))
    }

    func testRouletteControllerOwnsFirstResponderWhileVisible() {
        let controller = RecordingResponderViewController()

        XCTAssertTrue(controller.canBecomeFirstResponder)

        controller.viewDidAppear(false)
        XCTAssertEqual(controller.becomeFirstResponderCount, 1)
        XCTAssertEqual(controller.resignFirstResponderCount, 0)

        controller.viewWillDisappear(false)
        XCTAssertEqual(controller.becomeFirstResponderCount, 1)
        XCTAssertEqual(controller.resignFirstResponderCount, 1)
    }

    func testWinnerPresentationIsSingleFlightAcrossButtonAndShake() {
        let controller = RecordingWinnerPresentationViewController()
        controller.players.add(ParticipantListItem(name: "Hemal"))

        controller.clickBtn(self)
        controller.motionEnded(.motionShake, with: nil)
        XCTAssertEqual(controller.performedWinnerSegueCount, 1, "Concurrent winner inputs should request only one segue")

        controller.viewDidAppear(false)
        controller.motionEnded(.motionShake, with: nil)
        XCTAssertEqual(controller.performedWinnerSegueCount, 2, "Returning to the roulette should permit a later winner round")
    }

    func testParticipantItemAtIndexRejectsInvalidEntries() {
        let controller = ViewController()
        controller.players.add(NSString(string: "invalid"))

        XCTAssertNil(controller.participantItemAtIndex(-1), "Negative participant indexes should be ignored")
        XCTAssertNil(controller.participantItemAtIndex(0), "Non-participant entries should be ignored")
        XCTAssertNil(controller.participantItemAtIndex(1), "Out-of-range participant indexes should be ignored")
    }

    func testRemoveParticipantAtIndexRemovesValidEntry() {
        let controller = ViewController()
        controller.players.add(ParticipantListItem(name: "Hemal"))

        XCTAssertTrue(controller.removeParticipantAtIndex(0), "Valid participant indexes should be removable")
        XCTAssertEqual(controller.players.count, 0, "Removing a valid participant should update the player list")
    }

    func testRemoveParticipantAtIndexRejectsInvalidIndexes() {
        let controller = ViewController()
        controller.players.add(ParticipantListItem(name: "Hemal"))

        XCTAssertFalse(controller.removeParticipantAtIndex(-1), "Negative participant indexes should not be removed")
        XCTAssertFalse(controller.removeParticipantAtIndex(1), "Out-of-range participant indexes should not be removed")
        XCTAssertEqual(controller.players.count, 1, "Invalid participant indexes should leave the player list unchanged")
    }

    func testRemoveParticipantAtIndexRejectsInvalidEntryType() {
        let controller = ViewController()
        controller.players.add(NSString(string: "invalid"))

        XCTAssertFalse(controller.removeParticipantAtIndex(0), "Non-participant entries should not be removed through participant actions")
        XCTAssertEqual(controller.players.count, 1, "Rejected entries should remain untouched")
    }

    func testVisibleParticipantRowsIgnoreInvalidEntries() {
        let controller = ViewController()
        let first = ParticipantListItem(name: "Hemal")
        let second = ParticipantListItem(name: "Gareth")
        controller.players.add(NSString(string: "invalid"))
        controller.players.add(first)
        controller.players.add(NSNumber(value: 7))
        controller.players.add(second)

        XCTAssertEqual(controller.tableView(UITableView(), numberOfRowsInSection: 0), 2)
        XCTAssertTrue(controller.participantItemForVisibleRow(0) === first)
        XCTAssertTrue(controller.participantItemForVisibleRow(1) === second)
    }

    func testVisibleParticipantRowsIgnoreTypedEntriesWithoutVisibleNames() {
        let controller = ViewController()
        let visible = ParticipantListItem(name: "Gareth")
        controller.players.add(ParticipantListItem(name: ""))
        controller.players.add(ParticipantListItem(name: " \n\t "))
        controller.players.add(NSString(string: "invalid"))
        controller.players.add(visible)

        XCTAssertEqual(controller.tableView(UITableView(), numberOfRowsInSection: 0), 1)
        XCTAssertTrue(controller.participantItemForVisibleRow(0) === visible)
    }

    func testVisibleParticipantRemovalMapsToTypedEntry() {
        let controller = ViewController()
        let remaining = ParticipantListItem(name: "Gareth")
        controller.players.add(NSString(string: "invalid"))
        controller.players.add(ParticipantListItem(name: "Hemal"))
        controller.players.add(remaining)

        XCTAssertTrue(controller.removeParticipantForVisibleRow(0))
        XCTAssertEqual(controller.players.count, 2)
        XCTAssertTrue(controller.players.object(at: 0) is NSString, "Unrelated invalid entries should remain untouched")
        XCTAssertTrue(controller.participantItemForVisibleRow(0) === remaining)
    }

    func testVisibleParticipantRowsRejectInvalidIndexes() {
        let controller = ViewController()
        controller.players.add(NSString(string: "invalid"))
        controller.players.add(ParticipantListItem(name: "Hemal"))

        XCTAssertNil(controller.participantItemForVisibleRow(-1))
        XCTAssertNil(controller.participantItemForVisibleRow(1))
        XCTAssertFalse(controller.removeParticipantForVisibleRow(-1))
        XCTAssertFalse(controller.removeParticipantForVisibleRow(1))
        XCTAssertEqual(controller.players.count, 2)
    }

    func testConfigureWinnerDestinationRejectsUnexpectedDestination() {
        let controller = ViewController()

        XCTAssertFalse(controller.configureWinnerDestination(UIViewController()), "Unexpected winner destinations should be ignored")
    }

    func testConfigureWinnerDestinationSetsFallbackWithoutParticipants() {
        let controller = ViewController()
        let winner = WinnerViewController()

        XCTAssertTrue(controller.configureWinnerDestination(winner), "Winner destinations should be configured when the segue is wired correctly")
        XCTAssertEqual(winner.winnerName!, "Add participants first", "Empty participant lists should keep a visible fallback winner message")
    }

    func testConfigureWinnerDestinationSetsTypedParticipantWinner() {
        let controller = ViewController()
        let winner = WinnerViewController()
        controller.players.add(NSString(string: "invalid"))
        controller.players.add(ParticipantListItem(name: "Hemal"))

        XCTAssertTrue(controller.configureWinnerDestination(winner), "Winner destinations should accept valid winner controllers")
        XCTAssertEqual(winner.winnerName!, "Hemal", "Winner destinations should receive a typed participant winner")
    }

}

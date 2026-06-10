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

class CardRouletteTests: XCTestCase {

    func testParticipantNameNormalizationTrimsWhitespace() {
        XCTAssertEqual(ParticipantListItem.normalizedName("  Hemal\n")!, "Hemal", "Participant names should be trimmed before saving")
    }

    func testParticipantNameNormalizationRejectsBlankNames() {
        XCTAssertNil(ParticipantListItem.normalizedName("  \n\t  "), "Blank participant names should be ignored")
        XCTAssertNil(ParticipantListItem.normalizedName(nil), "Missing participant names should be ignored")
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
        controller.players.addObject(NSString(string: "invalid"))
        controller.players.addObject(item)
        let participantItems = controller.participantItems()

        XCTAssertEqual(participantItems.count, 1, "Invalid player entries should not participate in winner selection")
        XCTAssertTrue(participantItems[0] === item, "Valid participant entries should remain available")
    }

    func testParticipantItemAtIndexRejectsInvalidEntries() {
        let controller = ViewController()
        controller.players.addObject(NSString(string: "invalid"))

        XCTAssertNil(controller.participantItemAtIndex(-1), "Negative participant indexes should be ignored")
        XCTAssertNil(controller.participantItemAtIndex(0), "Non-participant entries should be ignored")
        XCTAssertNil(controller.participantItemAtIndex(1), "Out-of-range participant indexes should be ignored")
    }

    func testRemoveParticipantAtIndexRemovesValidEntry() {
        let controller = ViewController()
        controller.players.addObject(ParticipantListItem(name: "Hemal"))

        XCTAssertTrue(controller.removeParticipantAtIndex(0), "Valid participant indexes should be removable")
        XCTAssertEqual(controller.players.count, 0, "Removing a valid participant should update the player list")
    }

    func testRemoveParticipantAtIndexRejectsInvalidIndexes() {
        let controller = ViewController()
        controller.players.addObject(ParticipantListItem(name: "Hemal"))

        XCTAssertFalse(controller.removeParticipantAtIndex(-1), "Negative participant indexes should not be removed")
        XCTAssertFalse(controller.removeParticipantAtIndex(1), "Out-of-range participant indexes should not be removed")
        XCTAssertEqual(controller.players.count, 1, "Invalid participant indexes should leave the player list unchanged")
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
        controller.players.addObject(NSString(string: "invalid"))
        controller.players.addObject(ParticipantListItem(name: "Hemal"))

        XCTAssertTrue(controller.configureWinnerDestination(winner), "Winner destinations should accept valid winner controllers")
        XCTAssertEqual(winner.winnerName!, "Hemal", "Winner destinations should receive a typed participant winner")
    }

}
